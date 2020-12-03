import rules

# Create rule for ADG specific admin
is_bu_admin = rules.is_group_member('ADG Admins')

# Show Applications section on home screen
rules.add_perm('applications', rules.is_staff)

# User Applications
rules.add_perm('applications.view_userapplication', rules.is_staff)
rules.add_perm('applications.change_userapplication', rules.is_staff)
# rules.add_perm('applications.add_book', is_superuser)
# rules.add_perm('applications.change_book', is_superuser)
# rules.add_perm('applications.delete_book', rules.is_staff)

# Education
rules.add_perm('applications.view_education', rules.is_staff)
# rules.add_perm('applications.change_education', rules.is_staff)

# Work Experience
rules.add_perm('applications.view_workexperience', rules.is_staff)
# rules.add_perm('applications.change_workexperience', rules.is_staff)

# Business Line
rules.add_perm('applications.view_businessline', rules.is_staff)
# rules.add_perm('applications.change_businessline', rules.is_staff)

# Admin Note
rules.add_perm('applications.view_adminnote', rules.is_staff)
rules.add_perm('applications.add_adminnote', rules.is_staff)
rules.add_perm('applications.change_adminnote', rules.is_staff)
