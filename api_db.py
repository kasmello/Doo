import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPA_API = os.getenv('SUPA_API')
SUPA_URL = os.getenv('SUPA_URL')
supabase: Client = create_client(SUPA_URL,SUPA_API)

def insert_score(user_id, place_id, score):
    user_id = int(user_id)
    place_id = int(place_id)
    score = int(score)
    response = supabase.table('emoji_high_scores').select('score').eq("user_id", user_id).eq("place_id",place_id).execute()
    if len(response.data)==0:
        print(f'inserting new record for {user_id} at {place_id} into emoji')
        supabase.table('emoji_high_scores').insert({"user_id": user_id, "place_id": place_id, "score": score}).execute()
        return True
    elif response.data[0]['score'] < score:
        print(f'replace record for {user_id} at {place_id}')
        supabase.table('emoji_high_scores').update({"score": score}).eq("user_id", user_id).eq("place_id", place_id).execute()
        return True
    return False

def grab_top_5_place(place_id):
    response = supabase.table('emoji_high_scores').select('user_id','score').eq("place_id",place_id).order('score', desc=True).limit(5).execute()
    return response.data

def grab_top_5_global():
    response = supabase.table('emoji_high_scores').select('*').order('score', desc=True).limit(5).execute()
    return response.data  

if __name__ == '__main__':
    # print(insert_score(1,4,51))
    print(grab_top_5_global())
    # print(grab_top_5_place(3))