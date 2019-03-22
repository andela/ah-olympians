"""
the message function
"""
def email_message(slug,report_message):
    message = " This article with the following slug  " + slug + " has been reported because of\n " \
              + report_message 

    return message