import os
from MoinMoin.web.contexts import ScriptContext
request = ScriptContext()
from MoinMoin import user, wikiutil
the_user = user.User(request, auth_method="new-user")
the_user.name = "ExampleUser"
the_user.email = "ExampleUser@localhost"
the_user.enc_password = user.encodePassword("zoo0Eifi")
if (user.isValidName(request, the_user.name) and not user.getUserId(request, the_user.name) and not user.get_by_email_address(request, the_user.email)):
    print "This user with the userid %s doesn't exist yet."  % the_user.id
    the_user.save()
    filename = os.path.join(request.cfg.user_dir, the_user.id)
    if os.path.exists(filename):
        print "The user file %s was created" % filename
else:
    print "user credential already used - nothing done"