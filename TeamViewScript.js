var socketio;

function setup() {
    //setup global vars
    socketio = io.connect();

    //setup functions
    setupRoster();

}

function setupRoster(){
    let roster_table = document.getElementById("roster-table").getElementsByClassName("players")[0].getElementsByTagName("tbody")[0];

    socketio.emit("get-roster", {});

    socketio.on("roster-to-client", function(response){
        if(response.success){
            let players = response.players;
            for(let player in players){
                //create necessary table elements
                let table_row = document.createElement("tr");
                let first_name = document.createElement("td");
                let positions = document.createElement("td");
                let throws = document.createElement("td");
                let bats = document.createElement("td");
                let number = document.createElement("td");
                let player_class = document.createElement("td");

                //setup link for individual player pages
                let player_link = document.createElement("a");
                let full_name = players[player].first_name +" "+ players[player].last_name;
                let link_text = document.createTextNode(full_name);
                player_link.appendChild(link_text);
                player_link.setAttribute("href", `PlayerView.html?id=${players[player].id}`);
                player_link.title = full_name;

                //set table element values
                first_name.appendChild(player_link);
                positions.textContent = players[player].positions;
                player_class.textContent = players[player].class;
                throws.textContent = players[player].throws;
                bats.textContent = players[player].bats;
                number.textContent = players[player].number

                //place table elements in table row
                table_row.appendChild(number);
                table_row.appendChild(first_name);
                table_row.appendChild(positions);
                table_row.appendChild(player_class);
                table_row.appendChild(throws);
                table_row.appendChild(bats);

                //place table row in table
                roster_table.appendChild(table_row);
            }
        } else {
            console.log(response.message);
        }
    });
}