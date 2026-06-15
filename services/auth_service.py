from database.db_client import supabase


def sign_up(email, password):
    try:
        response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password
            }
        )
        return response
    except Exception as e:
        return str(e)


def sign_in(email, password):
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password
            }
        )
        return response
    except Exception as e:
        return str(e)


def sign_out():
    supabase.auth.sign_out()

def create_user_profile(user):
    existing = (
        supabase.table("users")
        .select("*")
        .eq("email", user.email)
        .execute()
    )

    if len(existing.data) == 0:
        supabase.table("users").insert(
            {
                "id": user.id,
                "email": user.email,
                "accepted_terms": True
            }
        ).execute()