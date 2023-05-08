start_message = r'''{
"blocks": [
{
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": "*Hyundai API Script run has been started.*\n\n:warning:  Ignore AWS Warning, script has started successfully.\n\n:hourglass:  Please allow for approximately 20 minutes for the run to complete"
    },
    "accessory": {
        "type": "image",
        "image_url": "https://lh3.googleusercontent.com/proxy/I1QilinkkV_kgEIUHiUGLyxmxvKt3wMCs9YLQ3Yr_HDh4l4g6TDvrCCrFMLMUkxnx5zlXp_fwMBMq3VWG2ebSiCd-yQMFW0",
        "alt_text": "gear"
    }
},
{
    "type": "divider"
}
]
}'''

exit_message = r'''{
"blocks": [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Your Hyundai API Files are ready:*"
        }
    },
    {
        "type": "divider"
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Run successfully completed!*\n\n Reminder to ensure images are updated in the drop folder."
        },
        "accessory": {
            "type": "image",
            "image_url": "https://pbs.twimg.com/profile_images/895269422960590848/SH2Fk7JC.jpg",
            "alt_text": "Haunted hotel image"
        }
    },
    {
        "type": "divider"
    }
]
}'''
