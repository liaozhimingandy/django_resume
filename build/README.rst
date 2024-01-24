
========= 
Resume
=========

Resume is a Django app to conduct web-based Resume.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "resumes" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "resumes",
    ]

2. Include the polls URLconf in your project urls.py like this::

    path("resumes/", include("resumes.urls")),

3. Run ``python manage.py migrate`` to create the resumes models.

4. Start the development server and visit http://localhost:8000/admin/
   to create a resume (you'll need the Admin app enabled).

5. Visit http://localhost:8000/resumes/ to participate in the resume.