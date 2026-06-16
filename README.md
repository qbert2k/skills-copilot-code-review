# GitHub Copilot Code Review

<img src="https://octodex.github.com/images/Professortocat_v2.png" align="right" height="200px" />

Hey qbert2k!

Mona here. I'm done preparing your exercise. Hope you enjoy! 💚

Remember, it's self-paced so feel free to take a break! ☕️

## Features

 - View all available extracurricular activities
 - Sign up for activities
 - Read the active announcement banner
 - Manage announcements from the signed-in teacher UI

## API Endpoints

 | Method | Endpoint                                                          | Description                                                         |
 | ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
 | GET    | `/activities`                                                     | Get all activities with their details and current participant count |
 | POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
 | GET    | `/announcements/active`                                           | Get the currently active announcement banner                       |
 | GET    | `/announcements?teacher_username=teacher`                         | List all announcements for the management dialog                   |
 | POST   | `/announcements?teacher_username=teacher`                         | Create a new announcement                                          |
 | PUT    | `/announcements/{announcement_id}?teacher_username=teacher`       | Update an announcement                                             |
 | DELETE | `/announcements/{announcement_id}?teacher_username=teacher`       | Delete an announcement                                             |

Activity, teacher, and announcement data are stored in MongoDB. The sample seed data is inserted automatically when the collections are empty.

## Announcement Rules

 - Announcements are database-driven and displayed from the active record in MongoDB.
 - Start dates are optional.
 - Expiration dates are required.
 - Only signed-in users can open the announcement manager and edit records.

