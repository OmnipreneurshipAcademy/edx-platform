#!/usr/bin/env bash

function show_help() {
    echo ""
    echo "Run all ADG tests inside openedx/adg/ including CMS, LMS and common. Generate coverage reports"
    echo "in XML and HTML format. Create junit-xml and diff-cover reports as well."
    echo "Usage:"
    echo "      ./adg_pipelines/scripts/run-adg-test.sh [branch-name]"
    echo "Options:"
    echo "      -h,     help                Print usage information"
    echo "              branch-name         Branch name for diff-cover [default: origin/master]"
    echo "Example:"
    echo "      ./adg_pipelines/scripts/run-adg-test.sh origin/develop"
    echo ""
}

if [ "$1" == "-h" ]; then
    show_help
    exit 0
fi

readonly LMS=lms
readonly CMS=cms
readonly FAIL_UNDER=20
branch="$1"

function run_adg_test() {
    echo "*** Running ${1} tests ***"
    # Run ADG tests and create (or append) coverage. Generate xml and html coverage files
    python -Wd -m pytest --ds="$1".envs.test --junitxml=reports/"$1"/nosetests.xml \
        openedx/adg/"$1" openedx/adg/common --cov --cov-config=setup.cfg --cov-config=tox.ini \
        --cov-config=adg_pipelines/.coveragerc-adg --cov-report xml --cov-report html $2
}

function generate_diff_cover_report() {
    echo "*** Generating diff-cover report ***"
    # Run ADG tests and create (or append) .coverage file
    EXIT_CODE=0
    DIFF_COVER_REPORT=$(diff-cover reports/coverage.xml --compare-branch="${1:-origin/master}" \
        --html-report reports/diff_coverage.html --fail-under="${2:-80}") || EXIT_CODE=$?
    export DIFF_COVER_REPORT
    # post comment to PR only from circleci
    [ "$CIRCLECI" ] && python3 adg_pipelines/scripts/post_comment.py -t ADG
    return $EXIT_CODE
}

[[ -n "$branch" && "$branch" != origin/* ]] &&
    echo "Invalid branch name. It must start with origin/..." && exit 1

rm -rf reports                                                   # First delete previous reports
run_adg_test $LMS                                                # Run test for LMS and LMS common
run_adg_test $CMS "--cov-append"                                 # Run test for CMS and LMS common
generate_diff_cover_report "${branch=origin/master}" $FAIL_UNDER # Generate reports
