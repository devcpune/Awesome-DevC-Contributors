import sys, json
from collections import OrderedDict
from operator import getitem
from re import search

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
    # Check if record exists
    if (username in data.keys()):
        raise LeaderbaordError("Record already exists please create a new issue to update the contributions.")

    # Add new record
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
Takes existing data of JSON file, username and PR information as input and updates a record to the JSON file
and returns the data of updated JSON file.
'''
def update_record(data,username,pr_dict):
    # Check if record exists
    if (username not in data.keys()):
        raise LeaderbaordError("Record does not exists please create a new issue to add a contribution.")

    # Update count 
    data[username]["count"] +=  len(pr_dict)
    # Add new contributions
    for name,link in pr_dict.items():
        data[username]["contributions"][name] = link
    # Sort records in reverse order
    data = OrderedDict(sorted(data.items(), 
                    key = lambda x: getitem(x[1], 'count'),reverse=True))
    # Write sorted records in JSON file
    with open("community-contributions.json","w") as write_file:
            json.dump(data,write_file,indent=2)

    return data

'''
Updates the leaderboard
'''

def update_leaderboard(data,start_marker,end_marker,file_name):

    with open(file_name,"r") as read_file:
        read_data = read_file.read()
        # Get index of starting of leaderboard records
        start = read_data.index(start_marker)+len(start_marker) 
        # Get index of ending of leaderboard records
        end = read_data.index(end_marker)
        write_data = read_data[:start]
        
    # Updating leaderboard from JSON file data
    # An empty list to store all the records
    records= []
    # Building string for record 
    for usr,info in contr_data.items():
        records.append(f"| [@{usr}](https://github.io/{usr}) | {info['count']} | <details> <summary>List of Contributions </summary>")
        for pr, link in info["contributions"].items():
            records.append(f" - [{pr}]({link}) <br>")
        records.append("</details> |\n")
    
    # Combining all the records in a final string
    write_data =  write_data+ "".join(records) + read_data[end:]

    # Writing on README file
    with open(file_name,"w") as write_file:
        write_file.write(write_data)

if __name__ == "__main__":

    try:
        
        issue_head = sys.argv[1].strip()
        issue_bod = sys.argv[2].strip() 
        # Get records from JSON file
        with open("community-contributions.json","r") as read_file:
            contr_data = json.load(read_file)

        # Create a dictionary
        pr_dict = {}
        for pr in issue_bod.split("\n"):
            # Assigning PR variables for PR name and link
            link = pr.split('|')[1].strip()
            link = (link.lstrip("**Link**: ")).strip()
            # If link is not valid
            if(search(r"^https://github.com/.+/.+/pull/\d+$",link) == None):
                raise LeaderbaordError("Link is not valid please create another issue with valid link.")

            pr_name = pr.split('|')[0].strip()
            pr_name = (pr_name.lstrip("**Name**: ")).strip()
            # Adding PR to the dictionary
            pr_dict[pr_name] = link
        
        # For adding new record 
        if issue_head.split("|")[0].lower() == "add":
            contr_data = add_record(contr_data,issue_head.split("|")[1],pr_dict)
        
        # For updating existing record
        elif issue_head.split("|")[0].lower() == "update":
            contr_data = update_record(contr_data,issue_head.split("|")[1],pr_dict)
        
        # Update the leader board 
        update_leaderboard(contr_data, 'Link of Contribution|\n| --- | --- | --- |\n', '<!-- End of Leaderbaord', 'README.md')        
        print("Successfully added your contribution")
    
    except LeaderbaordError as e:
        print("Something happened: ",str(e))

    except Exception as e:
        print("Internal error occured. Please try again later.")
