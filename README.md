## UK Election Analysis - Effect of Reform

### Project aims

* Setting up a project
* Github profile and setting linking up Git to PC/Github
* Scraping relevant data
* Plotting results
* Able to have an interactive plot
* serve to a webapp with Streamlit

### Getting a local shiny plot

* Create/open your python venv
* install pip, wheel, shiny, htmltools
* install the Shiny extension in VSCode, this will display plot within VSCode
* create and app.py file which contains the plot code
* run app.py to display 

### Setting up initial Shiny Python deploy

docs:  https://shiny.posit.co/py/docs/deploy-cloud.html

* create a python venv
* pip install rsconnect-python
* add an account to shiny apps, your details will be given when signing up
```
rsconnect add 
    --account <ACCOUNT> 
    --name <NAME> 
    --token <TOKEN> 
    --secret <SECRET>
```    
* compile a package in folder, BUT SAVE as requirements.txt
    * This is because shiny will take  your package requirements and build their own environment to handle the deployment
* deploy app by:

```
rsconnect deploy shiny /path/to/app --name <NAME> --title my-app
```
note: /path/to/app is just '.' if launching while in the same directory as the app.py