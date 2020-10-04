const season_selector = $('#season');
const game_selector = $('#game');
const team_selector = $("#team-selector");
const pitcher_selector = $("#pitcher");
const opponent_selector = $("#opponent");
const date_selector = $("#date");

// changes the pitcher choices based on the current team that is selected
const update_pitcher_choices = async () => {
    let response = await fetch(`/api/team/${team_selector.val()}/get_pitchers`);
    const pitchers = await response.json();
    if (pitchers.status != "success") {
        console.log("Error: " + pitchers.error);
        return;
    }
    pitcher_selector.empty();
    for (let pitcher of pitchers.data) {
        pitcher_selector.append(new Option(pitcher.name, pitcher.id));
    }
};

// gets all the game information by its id. If no id is provided, returns blank object
const get_game_by_id = async id => {
    const response = await fetch(`/api/game/${game_selector.val()}`);
    if (response.ok) {
        const game = await response.json();
        return game
    }
    return {}
};

const update_game_choices = async () => {
    const response = await fetch(`/api/season/${season_selector.val()}/games`);
    const games = await response.json();
    if (games.status != "success") {
        console.log("Error: " + response.error);
        return;
    }
    game_selector.empty();
    game_selector.append(new Option('', ''))
    for (let game of games.games) {
        game_selector.append(new Option(game.label, game.id));
    }
};

team_selector.change(async () => {
    update_pitcher_choices();

    const game = await get_game_by_id(game_selector.val())

    // if pitcher's team isn't WashU or matches game opponent, unselect game
    if (game.opponent_id != team_selector.val() && team_selector.val() != 1) {
        game_selector.val('');
    }

    // if team is not WashU, make opponent WashU
    if (team_selector.val() != 1) {
        opponent_selector.val(1);
    } else { // team is WashU, so just make opponent whatever game opponent is
        if (game_selector.val() != '') {
            opponent_selector.val(game.opponent_id);
        }
    }

});

date_selector.change(() => game_selector.val(''));

opponent_selector.change(async () => {
    // other teams can only pitch against us
    if (team_selector.val() != 1) {
        opponent_selector.val(1)
    }

    // if the opponent isn't the game opponent and its not Washu, unselect game
    const game = await get_game_by_id(game_selector.val())
    if (opponent_selector.val() != game.opponent_id) {
        game_selector.val('');
    }
})

season_selector.change(update_game_choices);

game_selector.change(async () => {
    if (game_selector.val() == '') {
        return;
    }

    const game = await get_game_by_id(game_selector.val());

    // match game and date
    date_selector.val(game.date);

    if (team_selector.val() == 1) { // if pitch is WashU, opponent is the game opponent
        opponent_selector.val(game.opponent_id);
    } else { // if its not, team is opponent of game and they are pitching against WashU
        opponent_selector.val(1);
        const prev_team = team_selector.val();
        team_selector.val(game.opponent_id);
        if (prev_team != game.opponent_id) {
            update_pitcher_choices();
        }
    }

    if (game.opponent_id == 1) { // if the opponent of the game is WashU, the pitcher is WashU
        team_selector.val(1);
    }
})