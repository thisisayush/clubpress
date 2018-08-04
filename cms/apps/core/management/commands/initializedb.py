from django.core.management.base import BaseCommand, CommandError
from apps.core.models import Options
from apps.core.utils import addOption, getOption, addDepartment, getDepartment, addBranch, getBranch

class Command(BaseCommand):

    help = "Initializes Database Tables with initial values"

    def handle(self, *args, **kwargs):
        
        options = (
            ("site_title", "Letstream", "Site Title"),
            ("support_email", "support@theletstream.com", "Support Email"),
            ("site_description", "Site Developed by Letstream.", "Site Description"),
            ("smtp_server", "mail.example.com", "SMTP Server"),
            ("smtp_user", "admin", "SMTP User"),
            ("smtp_pass", "pass", "SMTP Pass"),
            ("smtp_port", "000", "SMTP Port"),
            ("send_mails_as", "admin@localhost", "Send Mails As"),
            ("site_url", "http://localhost:8000", "Site Url"),
        )

        for option in options:
            if getOption(option[0]) == None:
                addOption(option[0], option[1], option[2])

        departments = [
            {
                "name": "Amity School of Engineering and Technology",
                "short_name": "ASET",
                "branches": [
                    {
                        "name": "ASET - CSE",
                        "short_name": "CSE"
                    },
                    {
                        "name": "ASET - IT",
                        "short_name": "IT"
                    },
                    {
                        "name": "ASET - Mechanical",
                        "short_name": "MECH"
                    },
                    {
                        "name": "ASET - Civil",
                        "short_name": "Civil"
                    }
                ]
            },
            {
                "name": "Amity Institute of Information Technology",
                "short_name": "AIT",
                "branches": [
                    {
                        "name": "AIT - BCA",
                        "short_name": "BCA"
                    },
                    {
                        "name": "AIT - B.Sc.(IT)",
                        "short_name": "BSC"
                    }
                ]
            }
        ]

        for dept in departments:
            d = getDepartment(dept['name'])
            if not d:
                d = addDepartment(dept['name'], dept['short_name'])
            else:
                print("%s Department Exists" % d.name)
            if not d:
                print("Unable to add department %s" % dept['name'])
            else:
                for branch in dept['branches']:
                    if not getBranch(branch['name']):
                        b = addBranch(branch['name'], branch['short_name'], d)
                        if not b:
                            print("Unable to add Branch %s" % branch['name'])
                    else:
                        print("Branch %s exists" % branch['name'])

        print("Added Initial Entries!")