import json

def __lb_file(guild_id: int) -> str:
	return "leaderboard{}.json".format(guild_id)

def __load_leaderboard(guild_id: int) -> dict:
	try:
		lbf = open(__lb_file(guild_id), 'r')
		return json.load(lbf)
	except:
		print("Creating new leaderboard")
		lb = dict()
		__save_leaderboard(lb, guild_id)
		return lb

def rankings(guild_id: int) -> list:
	lb = list(map(lambda e: (int(e[0]), e[1]), __load_leaderboard(guild_id).items()))
	return sorted(lb, key=lambda x: x[1], reverse=True)

def grant_points(user_id: int, points: int, guild_id: int):
	lb = __load_leaderboard(guild_id)
	try:
		lb[str(user_id)] += points
	except KeyError:
		lb[str(user_id)] = points
	lb[str(user_id)] = max(0, lb[str(user_id)])
	__save_leaderboard(lb, guild_id)

def __save_leaderboard(lb: dict, guild_id: int):
	with open(__lb_file(guild_id), 'w') as lbf:
		json.dump(lb, lbf)
