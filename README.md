
# OfflineParty

## Prerequisites:

1. Install the required dependencies (Python and the modules it needs) using the install script matching your OS
2. Alternatively, if you already have python installed or the installation of modules failed, just run ```pip install -r requirements.txt```
3. Create a Kemono/Coomer account and/or log in with your default browser **(Not needed if you search by user)**

## Instructions: 

1. [Download the latest release](https://github.com/2000GHz/OfflineParty/releases) in your preferred format (.7z or .zip)

2. Sign in to kemono.party or coomer.party (Or kemono.su / coomer.su)

3. Run `download.py` with your terminal (cmd on windows, terminal in unix) using your desired flags. Available flags are:
    - `-k` or `--kemono`: Download data from kemono
    - `-c` or `--coomer`: Download data from coomer
    - `-b` or `--both`: Download data from both kemono and coomer
    - `-l` or `--list`: Download from your own list of users/urls (user_list.txt in the Config folder, if it doesn't exist it will be created in the first run with this flag)
        - The txt file has to follow this structure:
        - ```
          UserOrUrl1
          UserOrUrl2
          UserOrUrl3
          ... 
    - `-r` or `--reset`: Reset (delete) the specific JSON files before downloading
    - -`u` or `--user`: Allows search for specific users by their username or URL, separated by commas and without spaces. (Incompatible with the other flags)
        - **WARNING, IF THE USERNAME HAS WHITESPACES IN THEIR NAME YOU HAVE TO USE THE COMMAND WITH QUOTES**
        - EXAMPLES:
        -     download.py -l "afrobull,Your Favorite Artist"
        -     download.py -l afrobull,vicineko,otakugirl90 (No whitespaces in their names, so no quotes needed)

4. Enjoy!

Note: You'll find a "content.txt" file inside every post's folder, inside it you'll find some relevant information such as the post URL, embedded content and comments where the artist could have included important information, make sure to check it out if you find an empty folder!

## Example of use

```bash
   python3 download.py -k -r
```
This will reset the `kemono_favorites.json` file, you can use this if for example you accidentally deleted a file, or new ones got added (For example if someone contributted with a higher tier )

You can use flags `-c`, `-b`, `-r` in a similar way.

** User search **
```bash
   python3 download.py -u otakugirl90
   python3 download.py -u https://kemono.party/discord/server/935649752475897936
```

Using this command will look through all creators, both kemono and coomer, to make sure we get all matching users.

Also, it's my first time working with shell scripts, so if you have any problems do let me know, thanks! 
