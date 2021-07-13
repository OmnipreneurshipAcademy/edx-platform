import datetime
import itertools

import ddt
import pytz
from crum import set_current_request
from six.moves import range

from capa.tests.response_xml_factory import MultipleChoiceResponseXMLFactory
from lms.djangoapps.courseware.tests.test_submitting_problems import ProblemSubmissionTestMixin
from lms.djangoapps.course_blocks.api import get_course_blocks
from openedx.core.djangolib.testing.utils import get_mock_request
from common.djangoapps.student.models import CourseEnrollment
from common.djangoapps.student.tests.factories import UserFactory
from xmodule.graders import ProblemScore
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase, SharedModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from xmodule.modulestore.tests.utils import TEST_DATA_DIR
from xmodule.modulestore.xml_importer import import_course_from_xml

from ...subsection_grade_factory import SubsectionGradeFactory
from ..utils import answer_problem, mock_get_submissions_score
import logging

log = logging.getLogger(__name__)


@ddt.ddt
class TestMultipleProblemTypesSubsectionScores(SharedModuleStoreTestCase):
    """
    Test grading of different problem types.
    """

    SCORED_BLOCK_COUNT = 7
    ACTUAL_TOTAL_POSSIBLE = 17.0

    @classmethod
    def setUpClass(cls):
        super(TestMultipleProblemTypesSubsectionScores, cls).setUpClass()
        cls.load_scoreable_course()
        chapter1 = cls.course.get_children()[0]
        cls.seq1 = chapter1.get_children()[0]

    def setUp(self):
        super(TestMultipleProblemTypesSubsectionScores, self).setUp()
        password = u'test'
        self.student = UserFactory.create(is_staff=False, username=u'test_student', password=password)
        self.client.login(username=self.student.username, password=password)
        self.addCleanup(set_current_request, None)
        self.request = get_mock_request(self.student)
        self.course_structure = get_course_blocks(self.student, self.course.location)

    @classmethod
    def load_scoreable_course(cls):
        """
        This test course lives at `common/test/data/scoreable`.

        For details on the contents and structure of the file, see
        `common/test/data/scoreable/README`.
        """

        course_items = import_course_from_xml(
            cls.store,
            'test_user',
            TEST_DATA_DIR,
            source_dirs=['scoreable'],
            static_content_store=None,
            target_id=cls.store.make_course_key('edX', 'scoreable', '3000'),
            raise_on_failure=True,
            create_if_not_present=True,
        )

        cls.course = course_items[0]

    def test_score_submission_for_all_problems(self):
        subsection_factory = SubsectionGradeFactory(
            self.student,
            course_structure=self.course_structure,
            course=self.course,
        )
        score = subsection_factory.create(self.seq1)

        log.error(f'\n\n\n\n \nPROBLEM_SCORES_KEYS\n{score.problem_scores.keys()}')
        log.error(f'\n\n\n\n \nPROBLEM_SCORES_VALUES\n{score.problem_scores.values()}')

        self.assertEqual(score.all_total.earned, 0.0)
        self.assertEqual(score.all_total.possible, self.ACTUAL_TOTAL_POSSIBLE)

        # Choose arbitrary, non-default values for earned and possible.
        earned_per_block = 3.0
        possible_per_block = 7.0
        with mock_get_submissions_score(earned_per_block, possible_per_block) as mock_score:
            # Configure one block to return no possible score, the rest to return 3.0 earned / 7.0 possible
            block_count = self.SCORED_BLOCK_COUNT - 1
            mock_score.side_effect = itertools.chain(
                [(earned_per_block, None, earned_per_block, None, datetime.datetime(2000, 1, 1))],
                itertools.repeat(mock_score.return_value)
            )
            score = subsection_factory.update(self.seq1)
        self.assertEqual(score.all_total.earned, earned_per_block * block_count)
        self.assertEqual(score.all_total.possible, possible_per_block * block_count)
