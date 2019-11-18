document.addEventListener('DOMContentLoaded', setup);

//global variables
var player_id = 1;
var player_first_name = "";
var player_last_name = "";
var player_positions = "";
var player_class = "";

var socketio;

function setup() {
  getVars();
  socketio = io.connect();

  getPlayerInfo();
}

function getPlayerInfo() {

  //request to server to emit player info
  socketio.emit("get-player-info", {
    player_id: player_id
  });

  //recieve server info on player
  socketio.on("player_info_to_client", function (response) {
    let data = JSON.parse(response.data)[0];
    // assign globals
    player_first_name = data.first_name;
    player_last_name = data.last_name;
    player_class = data.class;
    player_positions = data.positions;

    //begin filling user information
    let user_info_div = document.getElementsByClassName("user-info")[0];
    let first_name_p = user_info_div.getElementsByTagName("p")[0];
    let last_name_p = user_info_div.getElementsByTagName("p")[1];
    let class_p = user_info_div.getElementsByTagName("p")[2];
    let positions_p = user_info_div.getElementsByTagName("p")[3];

    let first_name_label = document.createElement("label");
    let last_name_label = document.createElement("label");
    let class_label = document.createElement("label");
    let positions_label = document.createElement("label");

    first_name_label.textContent = player_first_name;
    last_name_label.textContent = player_last_name;
    class_label.textContent = player_class;
    positions_label.textContent = player_positions;

    first_name_p.appendChild(first_name_label);
    last_name_p.appendChild(last_name_label);
    class_p.appendChild(class_label);
    positions_p.appendChild(positions_label);
  });

  //recieve server info for player measurables
  socketio.on("player_measurables_to_client", function (response) {
    if (response.success) {
      let data = JSON.parse(response.data);

      //begin filling measurable information
      let measurables_table = document.getElementsByClassName("raw-measurables")[0].getElementsByTagName("table")[0];
      for (let year in data) {
        let row_year = measurables_table.getElementsByTagName("tr")[0];
        let row_60_time = measurables_table.getElementsByTagName("tr")[1];
        let row_30_time = measurables_table.getElementsByTagName("tr")[2];
        let row_10_time = measurables_table.getElementsByTagName("tr")[3];
        let row_broad_jump = measurables_table.getElementsByTagName("tr")[4];
        let row_vert_jump = measurables_table.getElementsByTagName("tr")[5];
        let row_pro_agil = measurables_table.getElementsByTagName("tr")[6];
        let row_out_velo = measurables_table.getElementsByTagName("tr")[7];
        let row_in_velo = measurables_table.getElementsByTagName("tr")[8];
        let row_catch_velo = measurables_table.getElementsByTagName("tr")[9];
        let row_pop_time = measurables_table.getElementsByTagName("tr")[10];
        let raw_exit_velo = measurables_table.getElementsByTagName("tr")[11];

        let data_year = document.createElement("td");
        let data_60_time = document.createElement("td");
        let data_30_time = document.createElement("td");
        let data_10_time = document.createElement("td");
        let data_broad_jump = document.createElement("td");
        let data_vert_jump = document.createElement("td");
        let data_pro_agil = document.createElement("td");
        let data_out_velo = document.createElement("td");
        let data_in_velo = document.createElement("td");
        let data_catch_velo = document.createElement("td");
        let data_pop_time = document.createElement("td");
        let data_exit_velo = document.createElement("td");

        data_year.textContent = data[year].year;
        data_60_time.textContent = data[year].time_60;
        data_30_time.textContent = data[year].time_30;
        data_10_time.textContent = data[year].time_10;
        data_broad_jump.textContent = data[year].broad_jump;
        data_vert_jump.textContent = data[year].vertical_jump;
        data_pro_agil.textContent = data[year].pro_agility;
        data_out_velo.textContent = data[year].outfield_velo;
        data_in_velo.textContent = data[year].infield_velo;
        data_catch_velo.textContent = data[year].catcher_velo;
        data_pop_time.textContent = data[year].catcher_pop;
        data_exit_velo.textContent = data[year].exit_velo

        row_year.appendChild(data_year);
        row_60_time.appendChild(data_60_time);
        row_30_time.appendChild(data_30_time);
        row_10_time.appendChild(data_10_time);
        row_broad_jump.appendChild(data_broad_jump);
        row_vert_jump.appendChild(data_vert_jump);
        row_pro_agil.appendChild(data_pro_agil);
        row_out_velo.appendChild(data_out_velo);
        row_in_velo.appendChild(data_in_velo);
        row_catch_velo.appendChild(data_catch_velo);
        row_pop_time.appendChild(data_pop_time);
        raw_exit_velo.appendChild(data_exit_velo);
      }

      //attach input listener for measurables
      let measureable_input_button = document.getElementById("input-measurables-button");
      measureable_input_button.addEventListener("click", function (event) {

        let measurables_div = document.getElementsByClassName("raw-measurables")[0];
        let measurables_table = document.getElementsByClassName("raw-measurables")[0].getElementsByTagName("table")[0];
        addInputColumn(measurables_table);

        //hide input and edit buttons
        measureable_input_button.style.display = "none";
        let edit_button = document.getElementById("measureable-edit-button");
        if (typeof edit_button != undefined && edit_button != null){
          edit_button.style.display = "none";
        }

        //create submit info button if it does not exist
        let submit_info_button = document.getElementById("measurables_submit_info_button");
        if (typeof submit_info_button == undefined || submit_info_button == null) {
          submit_info_button = document.createElement("input");
          submit_info_button.setAttribute("type", "button");
          submit_info_button.setAttribute("id", "measurables_submit_info_button");
          submit_info_button.setAttribute("value", "submit");

          //add event listener to try to submit the new measurable data to sql
          submit_info_button.addEventListener("click", function (event) {
            let data = [];
            let measurables_table = document.getElementsByClassName("raw-measurables")[0].getElementsByTagName("table")[0];
            let rows = measurables_table.getElementsByTagName("tr");

            //creates an dictionary with year for every new column and changes row to a solid input
            let years_inputs = rows[0].getElementsByClassName("info-input");
            for (var index = 0; index < years_inputs.length; index++) {
              let input_year = years_inputs[index].firstChild.value;
              data.push({
                year: input_year
              });

              years_inputs[index].firstChild.remove();
              years_inputs[index].textContent = input_year;
            }

            //adds meta data to year headers and changes rows to solid data
            for (var index = 1; index < rows.length; index++) {
              let column_name = rows[index].getElementsByTagName("td")[0].textContent;
              let data_inputs = rows[index].getElementsByClassName("info-input");
              for (var i = 0; i < data_inputs.length; i++) {
                let value = data_inputs[i].firstChild.value;
                data[i][column_name] = value;

                data_inputs[i].firstChild.remove();
                data_inputs[i].textContent = value;
              }
            }

            //send to server to submit data to sql
            socketio.emit("submit-data-to-measurables", {
              player_id: player_id,
              data: data
            });

            //removes submit button
            submit_info_button.remove();

            //make edit and input buttons visible
            measureable_input_button.style.display = "inline";
            let edit_button = document.getElementById("measureable-edit-button");
            if (typeof edit_button != undefined && edit_button != null){
              edit_button.style.display = "inline";
            }
          });

          //attach button to the measurables div
          measurables_div.appendChild(submit_info_button);
        } else {
          console.log("submit info button exists");
        }
      });

      //attach edit listener for measurables if there is content to edit
      if (data.length > 0) {
        let measureable_edit_button = document.createElement("input");
        measureable_edit_button.setAttribute("type", "button");
        measureable_edit_button.setAttribute("id", "measureable-edit-button");
        measureable_edit_button.setAttribute("value", "Edit");


        //add event listener for edit button
        measureable_edit_button.addEventListener("click", function (event) {

          let measurables_table = document.getElementsByClassName("raw-measurables")[0].getElementsByTagName("table")[0];

          //make columns editable
          let rows = measurables_table.getElementsByTagName("tr");
          for (let index = 0; index < rows.length; index++) {

            let data_elements = rows.item(index).getElementsByTagName("td");
            for (var i = 1; i < data_elements.length; i++) {

              let value = data_elements[i].textContent;
              data_elements[i].textContent = "";
              data_elements[i].setAttribute("class", "edit-inputs");

              let field = document.createElement("input");
              field.setAttribute("type", "input");
              field.setAttribute("maxLength", "20");
              field.setAttribute("value", value);

              data_elements[i].appendChild(field);
            }
          }


          //create edit submit button
          let submit_edit_button = document.getElementById("measurables_submit_edit_info_button");

          //hide input and edit buttons
          measureable_input_button.style.display = "none";
          measureable_edit_button.style.display = "none";

          //make submit edit button if it does not exist already
          if (typeof submit_edit_button == undefined || submit_edit_button == null) {

            submit_edit_button = document.createElement("input");
            submit_edit_button.setAttribute("type", "button");
            submit_edit_button.setAttribute("id", "measurables_submit_edit_info_button");
            submit_edit_button.setAttribute("value", "submit");

            //attach event listener to edit button
            submit_edit_button.addEventListener("click", function(event){

              //change columns back into values and get values for data dict
              let edit_data = [];
              let measurables_table_rows = document.getElementsByClassName("raw-measurables")[0].getElementsByTagName("table")[0].getElementsByTagName("tr");

              //setup data array
              for(let j = 0; j < measurables_table_rows[0].getElementsByTagName("td").length-1; j++){
                edit_data.push({});
              }
              //add data to array
              for(let i = 0; i < measurables_table_rows.length; i++){

                let row = measurables_table_rows.item(i);
                let row_name = row.getElementsByTagName("td")[0].textContent;
                let inputs = row.getElementsByClassName("edit-inputs");

                for(let index=0; index<inputs.length; index++){

                  let value = inputs.item(index).firstChild.value;
                  inputs.item(index).firstChild.remove;
                  inputs.item(index).textContent = value;

                  edit_data[index][row_name] = value;
                }
              }

              //sends data to server for DB update
              console.log(edit_data);

              //brings back input button
              measureable_input_button.style.display = "inline";
              measureable_edit_button.style.display = "inline";

              //remove edit submit button
              submit_edit_button.remove();
            });

            //add button to page
            measurables_table.appendChild(submit_edit_button);
          }
        });

        document.getElementsByClassName("raw-measurables")[0].insertBefore(measureable_edit_button, measureable_input_button);
      }

    } else {
      console.log("response failure");
      console.log(response.message);
    }
  });
}

//gets the value of the get variables passed in the url
function getVars() {
  let variables = document.location.toString().split("?").pop().split("&");
  variables.forEach(function (item) {
    let var_name = item.split("=")[0];
    let var_value = item.split("=")[1];
    //assigns global variable to get variable in url
    if (var_name == "id") {
      player_id = var_value;
    }
  });
}

//adds a columnt to the passed table full of input values
function addInputColumn(table) {
  //<td>
  //  <input type="text" maxLength=10 />
  //</td>
  let rows = table.getElementsByTagName("tr");
  for (var index = 0; index < rows.length; index++) {
    let row = rows.item(index);

    let data = document.createElement("td");
    data.setAttribute("class", "info-input");

    let input = document.createElement("input");
    input.setAttribute("type", "text");
    input.setAttribute("maxLength", "20");

    data.appendChild(input);
    row.appendChild(data);
  }
}