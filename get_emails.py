from __future__ import print_function

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode

# for dealing with attachement MIME types

CWD = os.path.dirname(os.path.abspath(__file__))

# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES = ["https://mail.google.com/"]


def get_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = os.path.join(CWD, "token.json")
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(CWD, "credentials.json"), SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    service = build("gmail", "v1", credentials=creds)
    return service


service = get_service()


def search_messages(service, query):
    result = service.users().messages().list(userId="me", q=query).execute()
    messages = []
    if "messages" in result:
        messages.extend(result["messages"])
    while "nextPageToken" in result:
        page_token = result["nextPageToken"]
        result = (
            service.users()
            .messages()
            .list(userId="me", q=query, pageToken=page_token)
            .execute()
        )
        if "messages" in result:
            messages.extend(result["messages"])
    return messages


def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)


def parse_parts(service, parts, folder_name, message):
    """
    Utility function that parses the content of an email partition
    """
    for part in parts:
        filename = part.get("filename")
        mimeType = part.get("mimeType")
        body = part.get("body")
        data = body.get("data")
        if part.get("parts"):
            # recursively call this function when we see that a part
            # has parts inside
            parse_parts(service, part.get("parts"), folder_name, message)
        if mimeType == "text/plain":
            # if the email part is text plain
            if data:
                text = urlsafe_b64decode(data).decode()
                print(text)
        elif mimeType == "text/html":
            # if the email part is an HTML content
            # save the HTML file and optionally open it in the browser
            if not filename:
                filename = "index.html"
            filepath = os.path.join(CWD, folder_name, filename)
            print("Saving HTML to", filepath)
            with open(filepath, "wb") as f:
                f.write(urlsafe_b64decode(data))


def read_message(service, message):
    """
    This function takes Gmail API `service` and the given `message_id` and does the following:
        - Downloads the content of the email
        - Prints email basic information (To, From, Subject & Date) and plain/text parts
        - Creates a folder for each email based on the subject
        - Downloads text/html content (if available) and saves it under the folder created as index.html
        - Downloads any file that is attached to the email and saves it in the folder created
    """
    msg = (
        service.users()
        .messages()
        .get(userId="me", id=message["id"], format="full")
        .execute()
    )
    # parts can be the message body, or attachments
    print(msg.keys())
    payload = msg["payload"]
    print(payload.keys())
    headers = payload.get("headers")
    parts = payload.get("parts")
    if not parts:
        parts = [payload]
    folder_name = "email"
    has_subject = False
    if headers:
        # this section prints email basic info & creates a folder for the email
        for header in headers:
            name = header.get("name")
            value = header.get("value")
            if name.lower() == "from":
                # we print the From address
                print("From:", value)
            if name.lower() == "to":
                # we print the To address
                print("To:", value)
            if name.lower() == "subject":
                # make our boolean True, the email has "subject"
                has_subject = True
                # make a directory with the name of the subject
                folder_name = clean(value)
                # we will also handle emails with the same subject name
                folder_counter = 0
                while os.path.isdir(os.path.join(CWD, folder_name)):
                    folder_counter += 1
                    # we have the same folder name, add a number next to it
                    if folder_name[-1].isdigit() and folder_name[-2] == "_":
                        folder_name = f"{folder_name[:-2]}_{folder_counter}"
                    elif folder_name[-2:].isdigit() and folder_name[-3] == "_":
                        folder_name = f"{folder_name[:-3]}_{folder_counter}"
                    else:
                        folder_name = f"{folder_name}_{folder_counter}"
                os.mkdir(os.path.join(CWD, folder_name))
                print("Subject:", value)
            if name.lower() == "date":
                # we print the date when the message was sent
                print("Date:", value)
    if not has_subject:
        # if the email does not have a subject, then make a folder with "email" name
        # since folders are created based on subjects
        if not os.path.isdir(os.path.join(CWD, folder_name)):
            os.mkdir(os.path.join(CWD, folder_name))
    parse_parts(service, parts, folder_name, message)
    print("=" * 50)


def mark_read_messages(service, messages):
    service.users().messages().batchModify(
        userId="me",
        body={
            "ids": [m["id"] for m in messages],
            "removeLabelIds": ["UNREAD"],
        },
    ).execute()


def delete_messages(service, messages):
    service.users().messages().batchDelete(
        userId="me", body={"ids": [m["id"] for m in messages]}
    ).execute()


def cleanup_messages(serivce, messages):
    mark_read_messages(serivce, messages)
    delete_messages(serivce, messages)


if __name__ == "__main__":
    # get emails that match the query you specify
    results = search_messages(service, "from:readers@hellobooks.com")
    print(f"Found {len(results)} results.")
    # for each email matched, read it (output plain/text to console & save HTML and attachments)
    for msg in results:
        read_message(service, msg)
