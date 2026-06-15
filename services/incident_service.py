from database.db_client import supabase


def create_incident(data):

    return (
        supabase
        .table("incidents")
        .insert(data)
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