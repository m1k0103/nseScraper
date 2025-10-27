import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool, cpu_count


def getTeamLeaderboard(pageNum):
    url = f"https://tournaments.nse.gg/tournaments/counter-strike-2-nse-winter-25/teams/sort/name?page={pageNum}"
    
    raw_content = requests.get(url=url).text
    soup = BeautifulSoup(raw_content, "html.parser")

    teamnamesElements = soup.find_all("td", {"class": "teams-name"})
    allTeamNames = []
    for i in range(len(teamnamesElements)):
        s2 = BeautifulSoup(str(soup.find_all("td", {"class": "teams-name"})[i]), "html.parser")
        allTeamNames.append([s2.find("a").get_text().strip(), s2.find("a")["href"]])
    
    return allTeamNames #returns in 3d array in the following format [[name,url], ...]


def getTeamPlayers(teamurl):
    url = f"https://tournaments.nse.gg/{teamurl}"
    
    raw_text = requests.get(url=url).text
    soup = BeautifulSoup(raw_text, "html.parser")


    allPlayerData = []
    #get all player names, profile_urls and their role
    for playerHtml in soup.find_all("tr", {"class":"odd"}) + soup.find_all("tr", {"class":"even"}):
        playerSoup = BeautifulSoup(str(playerHtml), "html.parser")

        playerUrl = playerSoup.find("a")["href"]
        playerName = playerSoup.find("a").text.strip()
        playerRole = "Leader" if "Leader" in str(playerSoup) else "Player"
        allPlayerData.append([playerName, playerUrl, playerRole])
        print(playerName, playerUrl, playerRole)
        writePlayerDataToFile([playerName, playerUrl, playerRole])
    return allPlayerData # returns in format [[name,url,role], [...], ...]
    

def writePlayerDataToFile(data):
    with open("players.txt", "a", encoding="utf-8") as f:
        f.write(f"{data[0]} | {data[1]} | {data[2]}\n")



if __name__ == "__main__":
    # gets all teams from a leaderboard page
    all_teams = []
    for i in range(7):
        all_teams.extend(getTeamLeaderboard(i))

    # get only team urls and feed them into func which gets all players in each team
    team_urls = [i[1] for i in all_teams]
    with Pool(cpu_count()) as p:
        try:
            results = p.map(getTeamPlayers, team_urls)
        except IndexError as e:
            print(f"!!! IndexError occurred: {e}")
    # write all players to file
    #for i in results:
    #    writePlayerDataToFile(i)

    print("done")