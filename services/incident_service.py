from database.db_client import supabase


def create_incident(data):

    response = (
        supabase
        .table("incidents")
        .insert(data)
        .execute()
    )

    return response

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