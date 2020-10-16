# url_shortening_app

0- first download the dump of database and import it(username-root and password = "") and database name  = url_short_db
if you want to use something else you have to edit connection details in config file

To import the data .... go to the mysqlworkbench, open the localhost connection and go to the option server, there you will get the option data import,choose the option (import from self contained file) and select the path to the downloaded .sql file, then set database name as url_short_db and hit start import.


1- To run this flask app first create a virtual env using command -----> python3.6 -m venv env_name
   Now activate your virtual env using command source bin/activate and install the dependencies using requirements.txt file
   
example- 1-create virtual env named url_shortening_venv
         root@machli:/home/machli/workspace_nayan# python3.6 -m venv url_shortening_venv
         
         2- enter inside the virtaul env
         root@machli:/home/machli/workspace_nayan# cd url_shortening_venv
         
         3- git clone (path of the repository)
         
         3-activate the virtual env
         root@machli:/home/machli/workspace_nayan/url_shortening_venv# source bin/activate
         
         4-upgrade pip
         (url_shortening_env) root@machli:/home/machli/workspace_nayan/url_shortening_venv#pip install --upgrade pip
         
         5- install wheel
         (url_shortening_env) root@machli:/home/machli/workspace_nayan/url_shortening_venv#pip install wheel
         
         6- run app using command ----> gunicorn --bind 0.0.0.0:5009 wsgi:app
         (url_shortening_env) root@machli:/home/machli/workspace_nayan/url_shortening_venv# gunicorn --bind 0.0.0.0:5009 wsgi:app
         
         7-if your app starts you will see something like this
         
         (url_shortening_env) root@machli:/home/machli/workspace_nayan/ADDA/url_shortening_env# gunicorn --bind 0.0.0.0:5009 wsgi:app
        [2020-10-16 18:35:09 +0530] [13049] [INFO] Starting gunicorn 20.0.4
        [2020-10-16 18:35:09 +0530] [13049] [INFO] Listening at: http://0.0.0.0:5009 (13049)
        [2020-10-16 18:35:09 +0530] [13049] [INFO] Using worker: sync
        [2020-10-16 18:35:09 +0530] [13052] [INFO] Booting worker with pid: 13052
        
        
        8- this means app is running at http://0.0.0.0:5009
        
        9-Api for shortening the given url
        
        http://0.0.0.0:5009/url_shortening?url=https://www.google.com/
        here /url_shortening is the end point and key-url, value-https://www.google.com/(you can pass any url which you want to get shortened)
        
        response would be like:
        {
          "0": {
              "hourly_visits": {
                  "16": {
                      "count": 3
                  },
                  "18": {
                      "count": 1
                  }
              },
              "original_url": "https://www.google.com/",
              "short_url": "WR7",
              "total_visits": 4
          }
      }
      
      
      10- api which will redirect you to original url by using short url
      
      In the above response the you can see ----->  "short_url": "WR7"
      
      Now we will  use this short url as endpoint
      http://0.0.0.0:5009/WR7     (you will be redirected to google home page as this is the short url for that)
      
      
      
      11- search api
      
      
       http://0.0.0.0:5009/search?url_content=geek
       
       here /search is the end point, key=url_content, value = geek 
       
       This will return all the url having word geek in it 
       
       response would be :
       
       {
          "0": {
              "id": 7,
              "original_url": "https://practice.geeksforgeeks.org/courses/online",
              "short_url": "f48"
          },
          "1": {
              "id": 8,
              "original_url": "https://en.wikipedia.org/wiki/Geek",
              "short_url": "muP"
          },
          "2": {
              "id": 9,
              "original_url": "https://practice.geeksforgeeks.org/courses/",
              "short_url": "pUO"
          }
      }
      
      
      
      
      

