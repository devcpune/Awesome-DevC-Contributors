import sys, json, datetime, requests
from collections import OrderedDict
from operator import getitem
from re import search
from github import Github

'''
Class to raise error if everything there is some problem in processing even if everyting is syntactically correct. 
'''
class LeaderbaordError(Exception):
    def __init__(self,message):
        self.message = message
        super().__init__(self.message)


'''
Takes existing data of JSON file, username and PR information as input and adds a record to the JSON file
and returns the data of updated JSON file.
'''
def add_record(data,username,pr_dict):
    
    # Add new record or update existing record
    data[username] = {"count": len(pr_dict),
                      "contributions": pr_dict
                    }
    # Sort records in reverse order
    data = OrderedDict(sorted(data.items(), 
                    key = lambda x: getitem(x[1], 'count'),reverse=True))
    # Write sorted records in JSON file
    with open("community-contributions.json","w") as write_file:
            json.dump(data,write_file,indent=2)
    return data


'''
Function to get PR object through github API based on supplied html url
'''
def get_pr_by_html(html,g):
    html = html[len("https://github.com/"):]
    org,repo,temp,pr_id = html.split("/")
    repo = g.get_repo(f"{org}/{repo}")
    return repo.get_pull(int(pr_id))


'''
Function to check if the link supplied for PR is working, belongs to the user and is made in the given duration.
'''
def get_pr_title(html,username,start_date,end_date,g):
    # If link points to a page which does not exists
    if((search(r"^https://github.com/.+/.+/pull/\d+$",html) == None) or (requests.get(html).status_code != 200)):
        raise LeaderbaordError(f"Link:{html} is not valid please edit the issue with valid link.")
    # If link is valid get the PR object through github API
    pr_obj = get_pr_by_html(html,g)
    # If PR is no created by given  user
    if(pr_obj.user.login != username):
        raise LeaderbaordError(f"The PR: {html} is not created by {username}")
    # If PR is not created in given time period
    if(pr_obj.created_at < start_date or pr_obj.created_at > end_date):
        raise LeaderbaordError(f"The PR {html} was not created during Open Source Immersion Programme")
    
    # If PR is valid according to all the above mentioned criterias, return `True`
    return pr_obj.title

'''
Updates the leaderboard
'''

def update_leaderboard(data,start_marker,end_marker,file_name,issue_number):

    with open(file_name,"r") as read_file:
        read_data = read_file.readlines()
        # Get index of starting of leaderboard records
        start = (read_data).index(start_marker) + 2 # line after table header
        # Get index of ending of leaderboard records
        end = (read_data).index(end_marker) + 2 # line after end of table
        write_data =  "".join(read_data[:start])
        
    # Updating leaderboard from JSON file data
    # An empty list to store all the records
    records= []
    # generating id for issue
    issue_number = str(issue_number).zfill(4)
    # Building string for record 
    for usr,info in data.items():
        records.append(f"| [@{usr}](https://github.io/{usr}) | {info['count']} | <details> <summary>List of Contributions </summary>")
        for link, pr in info["contributions"].items():
            records.append(f" - [{pr}]({link}) <br>")
        records.append("</details> |\n")
    
    # Combining all the records in a final string
    write_data =  write_data+"".join(records)+end_marker+f"New to the repository? click [here](https://github.com/devcpune/Awesome-DevC-Contributors/issues/new?assignees=&labels=&template=new-contributor.md&title=add|{issue_number}) to add your contribution.\n"
    write_data = write_data+"".join(read_data[end:])

    # Writing on README file
    with open(file_name,"w") as write_file:
        write_file.write(write_data)


if __name__ == "__main__":
    try:
        
        username = sys.argv[1].strip()
        links = (sys.argv[2].strip()).split("\n")
        g = Github()
        # Get records from JSON file
        with open("community-contributions.json","r") as read_file:
            contr_data = json.load(read_file)

        # Create a dictionary
        pr_dict = {}
        # Validating the link
        start_date = datetime.datetime(2020,7,15,00,00)
        end_date = datetime.datetime(2020,8,16,00,00)
        g = Github()
        for link in links:
            # Removing any extra spaces from the link
            link = link.strip()
            title = get_pr_title(link,username,start_date,end_date,g)
            # Adding PR to the dictionary
            pr_dict[link] = title
        
        # For adding new record 
        contr_data = add_record(contr_data,username,pr_dict)
        
        # Update the leader board
        # Genrating issue number for the link 
        repo = g.get_repo("devcpune/Awesome-DevC-Contributors")
        issues =  repo.get_issues(state='all')
        issue_number= list(issues)[0].number + 1 # The first element of issue list is the latest issue
        update_leaderboard(contr_data, '| Name | Number of Contributions | Link of Contribution|\n', '<!-- End of Leaderbaord-->\n', 'README.md',issue_number)        
        
        print("Successfully added your contribution")
    
    except LeaderbaordError as e:
        print(str(e))
    except Exception as e:
        print("Internal error occured. Please try again later.")
    