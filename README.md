# P5 Item Catalog

## Introduction

This is the project 5 Item Catalog App for Udacity Fullstack Nanodegree. This app covers the basics features such as...
- Working with CRUD
- Making a webserver
- Using flask framework
- Authentication and Authorization
- Using 3rd party authentication apps


## Requirements

* python >= 2.7
* Oracle VM VirtualBox software
* Vagrant software
* Git software


## Installation

1. Clone or fork this repository
2. Download and Install Oracle VM software
3. Download and Install Vagrant software
4. Download and Install Git

##Usage

1. Open up Git Bash
2. Using Git command line. change directory through files until you're in the vagrant file. I.E. 'Root Folder/Vagrant/'
    * NOTE: You'll know if you're in the right directory when you see files like .vagrant, Vagrantfile, seed.py, project.py
3. Once in Vagrant directory, type 'vagrant up' into terminal to install files
4. Next, type 'vagrant ssh' to login
5. You're now logged into the virtual machine, type 'cd /vagrant'
6. Type 'python database_setup.py' to create database file
7. Type 'python seed.py' to file database with data
8. Type 'python project.py' to run project file
9. In any browser, Type 'localhost:8000' to view page
10. Type '\exit' to logout


## Details

* This application allows the user to insert new collections and artworks and retrieve them from database. 
