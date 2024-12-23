import boto3
import re
from datetime import timedelta

def parse_expiration(input_str):
    match = re.match(r"(\d+)([dh])", input_str)
    if not match:
        raise ValueError("Invalid input. Please specify time as '1h' for 1 hour or '1d' for 1 day.")

    value, unit = match.groups()
    value = int(value)
    if unit == 'h':
        return value * 3600  # seconds in an hour
    elif unit == 'd':
        return value * 86400  # seconds in a day


def list_buckets():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    return buckets


def generate_presigned_urls(bucket_name, expiration, html_filename, txt_filename):
    s3 = boto3.client('s3')

    prefixes = set()
    objects = []

    response = s3.list_objects_v2(Bucket=bucket_name)
    while response.get('Contents'):
        for obj in response['Contents']:
            key = obj['Key']
            if '/' in key:
                prefixes.add(key.split('/')[0])
            objects.append(key)

        if response.get('IsTruncated'):
            response = s3.list_objects_v2(Bucket=bucket_name, ContinuationToken=response['NextContinuationToken'])
        else:
            break

    html_content = "<html><body><h1>Download Links</h1>\n"
    text_content = ""

    for prefix in sorted(prefixes):
        html_content += f"<h2>Prefix: {prefix}</h2>\n"
        for obj in objects:
            if obj.startswith(prefix):
                try:
                    presigned_url = s3.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': bucket_name, 'Key': obj},
                        ExpiresIn=expiration
                    )
                    print(f"Generated URL for {obj}: {presigned_url}")
                except Exception as e:
                    print(f"Error generating URL for {obj}: {e}")
                    continue
                html_content += f"<a href='{presigned_url}'>{obj}</a><br>\n"
                text_content += f"{presigned_url}\n"

    html_content += "</body></html>"

    with open(html_filename, "w") as html_file:
        html_file.write(html_content)

    with open(txt_filename, "w") as text_file:
        text_file.write(text_content)


def main():
    s3 = boto3.client('s3')
    buckets = list_buckets()

    print("Available Buckets:")
    for i, bucket in enumerate(buckets):
        print(f"{i + 1}. {bucket}")

    selected_buckets = input("Enter bucket numbers (comma-separated, e.g., 1,3): ").strip()
    bucket_indices = [int(x) - 1 for x in selected_buckets.split(',')]
    chosen_buckets = [buckets[i] for i in bucket_indices]

    if len(chosen_buckets) > 1:
        combined_report = input("Do you want a combined report for all buckets? (yes/no): ").strip().lower() == "yes"
    else:
        combined_report = False

    expiration_input = input("Enter expiration time (e.g., '1h' for 1 hour, '1d' for 1 day): ").strip()
    try:
        expiration = parse_expiration(expiration_input)
    except ValueError as e:
        print(e)
        return

    if combined_report:
        html_filename = "download-links-combined.html"
        txt_filename = "download-links-combined.txt"
        with open(html_filename, "w") as html_file, open(txt_filename, "w") as txt_file:
            html_file.write("<html><body><h1>Combined Download Links</h1>\n")
            for bucket in chosen_buckets:
                html_file.write(f"<h2>Bucket: {bucket}</h2>\n")
                txt_file.write(f"Bucket: {bucket}\n")
                generate_presigned_urls(bucket, expiration, html_file.name, txt_file.name)
                html_file.write("<hr>\n")
            html_file.write("</body></html>")
    else:
        for bucket in chosen_buckets:
            html_filename = f"download-links-{bucket}.html"
            txt_filename = f"download-links-{bucket}.txt"
            print(f"Generating report for bucket: {bucket}")
            generate_presigned_urls(bucket, expiration, html_filename, txt_filename)

    print("Pre-signed URLs generated successfully!")
    if combined_report:
        print(f"- Combined links saved in '{html_filename}' and '{txt_filename}'")
    else:
        print("- Separate reports created for each bucket.")

if __name__ == "__main__":
    main()

