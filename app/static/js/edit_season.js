function deleteSeasonOnly(id) {
    let deleteSeason = confirm("Are you sure you want to delete the season?");
    if (deleteSeason) {
        window.location.href = `/delete_season/${id}/no`;
    }
}
function deleteSeasonAndAllOtherData(id) {
    let deleteSeason = confirm("Are you sure you want to delete the season and all data associated with it?");
    if (deleteSeason) {
        window.location.href = `/delete_season/${id}/yes`;
    }
}