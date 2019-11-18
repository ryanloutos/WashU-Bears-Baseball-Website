var http = require("http"),
  fs = require("fs"),
  url = require("url"),
  mysql = require("mysql"),
  socketio = require("socket.io");

var connection;

setupMYSQL();

var app = http.createServer(function(req, resp){
  if(req.url.split(".").reverse()[0]==="css") {
		fs.readFile("."+req.url,(err,data) => {
			// This callback runs when the client.css file has been read from the filesystem.
			if(err) return resp.writeHead(500);
			resp.writeHead(200,{"Content-type": "text/css"});
			resp.end(data);
		});
	}else if(req.url.split(".").reverse()[0]==="js"){
    fs.readFile("."+req.url,(err,data) => {
			// This callback runs when the client.css file has been read from the filesystem.
			if(err) return resp.writeHead(500);
			resp.writeHead(200,{"Content-type": "text/javascript"});
			resp.end(data);
		});
  }
	else {
    var q = url.parse(req.url, true);
    var filename = "." + q.pathname;
		fs.readFile(filename, function(err, data){
		// This callback runs when the client.html file has been read from the filesystem.
			if(err) return resp.writeHead(500);
			resp.writeHead(200);
      resp.end(data);
		});
	}
});
app.listen(3456);

//socket functions
var io = socketio.listen(app);
io.sockets.on("connection", function(socket){

  //sends roster to any socket that requests it
  socket.on("get-roster", function(data){
    getRoster(socket, "Wash U");
  });
  
  //sends player info and measurables to a socket that requests it
  socket.on("get-player-info", function(data){
    getPlayerMeasurables(socket, data['player_id']);
    getPlayerInfo(socket, data['player_id']);
  })

  //listens for input data to come in to place into measurables
  socket.on("submit-data-to-measurables", function(data){
    submitDataToMeasurables(socket, data['player_id'], data['data']);
  })
});

function setupMYSQL(){
  var mysql = require("mysql");
  connection = mysql.createConnection({
    host: "localhost",
    database: "Baseball",
    user: "admin",
    password: "admin"
  });
  //check mysql connection for errors
  connection.connect(function(err) {
      if (err){
        throw err;
      } 
      console.log("Connected!");
  });
}

function getRoster(socket, team="Wash U"){
  connection.query({
    sql: "SELECT * FROM Players WHERE team=? ORDER BY number",
    values: [team]
  }, function(errors, results, fields){
    if (errors) throw errors;
    let players_data = [];
    results.forEach(function(item){
      players_data.push({
        first_name:item.first_name,
        last_name: item.last_name,
        class: item.class,
        positions:item.positions,
        throws:item.throws,
        bats:item.bats,
        number:item.number,
        id:item.id
      });
    });
    socket.emit("roster-to-client", {success:true, players:players_data});
  });
}

function getPlayerMeasurables(socket, player_id){
  connection.query({
    sql: "SELECT * FROM measurables WHERE player_id=? ORDER BY year",
    values: [player_id]
  }, function(errors, results, fields){
    if(errors) throw errors;
    let ret_arr = {
      success: true,
      data: JSON.stringify(results)
    };
    socket.emit("player_measurables_to_client", ret_arr);
  });
}

function getPlayerInfo(socket, player_id){
  connection.query({
    sql:"SELECT * FROM Players WHERE id=?",
    values:[player_id]
  },function(errors, results, fields){
    if (errors) throw errors;
    let ret_arr = {
      success: true,
      data: JSON.stringify(results)
    };
    socket.emit("player_info_to_client", ret_arr);
  });

}

function submitDataToMeasurables(socket, player_id, data){

  //submit info to DB via node.js and MYSQL
  data.forEach(function(item){
    connection.query({
      sql: "INSERT INTO `measurables` (`player_id`, `year`, `time_60`, `time_30`, `time_10`, `broad_jump`, `vertical_jump`, `pro_agility`, `outfield_velo`, `infield_velo`, `catcher_velo`, `catcher_pop`, `exit_velo`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      values: [
        player_id,
        item['year'],
        item['60 time'],
        item['30 time'],
        item['10 time'],
        item['Broad Jump'],
        item['Vertical Jump'],
        item['5-10-5 time'],
        item['Outfield Velo\'s'],
        item['Infield Velo\'s'],
        item['Catcher Velo'],
        item['Pop Time'],
        item['Exit Velo']
      ]
    }, function(errors, results, fields){
      if (errors) throw errors;
      else {
        console.log("Successfully loaded new measurable to player: "+ player_id);
      }

    });
  });
}