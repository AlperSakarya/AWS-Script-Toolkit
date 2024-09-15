import boto3

def get_log_groups():
    log_groups = []
    logs_client = boto3.client('logs')
    paginator = logs_client.get_paginator('describe_log_groups')
    for page in paginator.paginate():
        log_groups.extend(page['logGroups'])
    return log_groups

def abbreviate_log_group_name(name):
    if len(name) > 80:
        return name[:25] + '.......' + name[-50:]
    else:
        return name

def display_log_groups(log_groups):
    print_ascii_art()
    print("\nFirst 10 Log Groups:")
    header_format = "{:<5} {:<80} {:<15}"
    row_format = "{:<5} {:<80} {:<15}"
    print(header_format.format("No.", "Log Group Name", "Retention"))
    print("-" * 100)
    for i, log_group in enumerate(log_groups[:10], 1):
        name = abbreviate_log_group_name(log_group['logGroupName'])
        retention = log_group.get('retentionInDays', 'Never Expire')
        if retention != 'Never Expire':
            retention = f"{retention} days"
        print(row_format.format(i, name, retention))

def summarize_retention_policies(log_groups):
    retention_counts = {}
    for log_group in log_groups:
        retention = log_group.get('retentionInDays', 'Never Expire')
        retention_counts[retention] = retention_counts.get(retention, 0) + 1
    print("\nRetention Policy Summary:")
    for retention, count in retention_counts.items():
        if retention == 'Never Expire':
            print(f"{count} log groups set to Never Expire")
        else:
            print(f"{count} log groups set to expire in {retention} days")

def set_retention_policy(log_groups, retention_days):
    logs_client = boto3.client('logs')
    count = 0
    for log_group in log_groups:
        if 'retentionInDays' not in log_group:
            name = log_group['logGroupName']
            logs_client.put_retention_policy(
                logGroupName=name,
                retentionInDays=retention_days
            )
            count += 1
    print(f"\nRetention policy set to {retention_days} days for {count} log groups that were set to Never Expire.")

def print_ascii_art():
    print(r"""

 _____ _    _   _                   _____ _ _           _             _             
/  __ \ |  | | | |                 |  ___| (_)         (_)           | |            
| /  \/ |  | | | |     ___   __ _  | |__ | |_ _ __ ___  _ _ __   __ _| |_ ___  _ __ 
| |   | |/\| | | |    / _ \ / _` | |  __|| | | '_ ` _ \| | '_ \ / _` | __/ _ \| '__|
| \__/\  /\  / | |___| (_) | (_| | | |___| | | | | | | | | | | | (_| | || (_) | |   
 \____/\/  \/  \_____/\___/ \__, | \____/|_|_|_| |_| |_|_|_| |_|\__,_|\__\___/|_|   
                             __/ |                                                  
                            |___/                                                   
  """)

def main():
    log_groups = get_log_groups()
    display_log_groups(log_groups)
    summarize_retention_policies(log_groups)

    while True:
        print("\nCloudWatch Log Eliminator")
        print("1. Set retention policy to 1 week for log groups set to Never Expire")
        print("2. Exit")
        choice = input("Please enter your choice: ")
        if choice == '1':
            set_retention_policy(log_groups, 7)
            # Update the log groups to reflect the changes
            log_groups = get_log_groups()
            summarize_retention_policies(log_groups)
        elif choice == '2':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()

