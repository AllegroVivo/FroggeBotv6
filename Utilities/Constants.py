################################################################################
### Numerical Constants ###
# System
MAX_EMBED_LENGTH = 6000
MAX_SELECT_OPTIONS = 24

# VIPs
DEFAULT_VIP_WARNING_DAYS = 3
MAX_VIP_WARNING_DAYS = 7
DEFAULT_VIP_MEMBERSHIP_LENGTH_DAYS = 30

# Scheduling
DEFAULT_SCHEDULE_LOCK_MINUTES = 0
MAX_SCHEDULE_LOCK_MINUTES = 60
DEFAULT_SCHEDULE_NOTIFY_MINUTES = 180

# Events
MAX_CONCURRENT_EVENTS = 10  # TODO: Implement this
MAX_SHIFT_BRACKET_COUNT = 5
MAX_SECONDARY_ELEMENT_COUNT = 20

# Staffing
MAX_CHARACTERS_PER_STAFF = 10
MAX_APPLICATION_QUESTIONS = 20
MAX_APPLICATION_SELECT_OPTIONS = 20

# Profiles
MAX_ADDITIONAL_IMAGES = 3

# Activities
MAX_CONCURRENT_ACTIVITIES_PER_TYPE = 10
MAX_RAFFLE_ENTRIES = 999999999
MAX_ACTIVITY_ENTRIES = 50
MAX_CONTEST_JUDGES = 10
MAX_CONTEST_CRITERIA = 20
MAX_CONTEST_ATTACHMENTS = 5

# Time Clock
DEFAULT_CLOCK_THRESHOLD_MINUTES = 15

# Forms
MAX_FORMS = 20
MAX_FORM_QUESTIONS = 20
MAX_FORM_NOTIFICATIONS = 10
MAX_QUESTION_OPTIONS = 20

################################################################################
### String Constants ###
# VIPs
DEFAULT_VIP_WARNING_TITLE = "VIP Warning"
DEFAULT_VIP_WARNING_DESCRIPTION = "Your VIP status is about to expire. Please renew it to continue enjoying the benefits."
DEFAULT_VIP_WARNING_THUMBNAIL = None

DEFAULT_VIP_EXPIRY_TITLE = "VIP Membership Expired"
DEFAULT_VIP_EXPIRY_DESCRIPTION = "Your VIP status has expired. Please renew it to continue enjoying the benefits."
DEFAULT_VIP_EXPIRY_THUMBNAIL = None

# Activities
DEFAULT_ACTIVITY_WIN_TITLE = "YOU WON!"
# (0: Activity Type, 1: Activity Name, 2: Prize)
DEFAULT_ACTIVITY_WIN_DESCRIPTION = (
    f"You have won the {0} `{1}` for the prize of **`{2}`**!\n\n"

    f"Please contact management or a host to claim your prize!"
)
DEFAULT_ACTIVITY_WIN_THUMBNAIL = None
################################################################################
