Getting Started
===============

Some basic docs on getting started with the project

- Create a virtualenv
- Clone the repo
- Install requirements `pip install -r requirements.txt`
- Setup database and other options in `prod.ini`
- *Need* to find a better way to get the specific host setup in fabric
- `fab dev db_init`
- `fab dev db_upgrade`
- `paster server --reload development.ini`
