from database.db_client import supabase


def create_incident(data):
    try:
        # Attempt primary insert with all columns
        return (
            supabase
            .table("incidents")
            .insert(data)
            .execute()
        )
    except Exception as e:
        # Defensive fallback if reporter columns are missing in the database
        safe_data = {k: v for k, v in data.items() if k not in ["reporter_name", "reporter_phone"]}
        return (
            supabase
            .table("incidents")
            .insert(safe_data)
            .execute()
        )


def update_incident(
        incident_id,
        data
):

    return (
        supabase
        .table("incidents")
        .update(data)
        .eq("id", incident_id)
        .execute()
    )


def get_all_incidents():

    return (
        supabase
        .table("incidents")
        .select("*")
        .order(
            "created_at",
            desc=True
        )
        .execute()
    )


def get_incident_by_id(
        incident_id
):

    return (
        supabase
        .table("incidents")
        .select("*")
        .eq("id", incident_id)
        .single()
        .execute()
    )


def delete_incident(
        incident_id
):

    return (
        supabase
        .table("incidents")
        .delete()
        .eq("id", incident_id)
        .execute()
    )
def get_user_incidents(user_id):

    return (
        supabase
        .table("incidents")
        .select("*")
        .eq("user_id", user_id)
        .order(
            "created_at",
            desc=True
        )
        .execute()
    )