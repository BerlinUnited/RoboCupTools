function PeriodicPlayer(player) 
{ 
  this.player = player;    
  this.currentStopListener = null;

  this.setPeriod = function(start,end) 
  {
    player.pause();
    if(this.currentStopListener != null) {
      this.player.media.removeEventListener("timeupdate", this.currentStopListener, false);
    }
    
    this.currentStopListener = function(event) {
     if (player.node.currentTime > end) {
          player.setCurrentTime(start);
          player.pause();
      }
    };
    
    player.media.addEventListener("timeupdate", this.currentStopListener, false);
    player.setCurrentTime(start);
  }
}

var playerGlobal;
$( document ).ready(function() {
  $('#player').mediaelementplayer({
    stretching: 'responsive',
    success: function(media, node, player) {
      $('#' + node.id + '-mode').html('mode: ' + player.pluginType);
      
      media.addEventListener('loadedmetadata', function() {
        playerGlobal = new PeriodicPlayer(player);
      });
    }
  });
});


var app = angular.module('test', ['schemaForm']);

app.controller('MainController', function($rootScope, $scope, $compile) {

  $scope.model = [];
  $scope.selected = null;

  var url = new URL(window.location.href);
  $scope.widget = { title: url.searchParams.get("name") !== null ? url.searchParams.get("name") : 'New' };

  /*
  $scope.openFile = function(input) {
  
    var reader = new FileReader();
    
    reader.onload = function(){
      jsonData = JSON.parse(reader.result);
      $scope.model = jsonData;
      
      for (var i = 0; i < jsonData.intervals.length; i++) 
      {
        var v = jsonData.intervals[i];
        if (typeof v.labels === 'undefined') {
          v.labels = {};
        }
        $scope.addPeriod(v);
      }
      
      $('[data-toggle="tooltip"]').tooltip();
    };
    reader.readAsText(input.files[0]);
  };
  */
  
  $scope.addLogfileToModel = function(id, data) 
  {
    $scope.model.push({"id":id, "data":data});
  }
  
  $scope.addPeriod = function(timeline, interval_id, data, log_offset, video_offset) 
  {
    var interval = data.intervals[interval_id];
    var offset = video_offset - log_offset;
    var width = (interval.end - interval.begin) / (data.end - log_offset) * 100;
    var starting_at = (interval.begin - log_offset) / (data.end - log_offset) * 100;

    var str = '<a href="#" id="'+interval_id+'" class="button '+interval.type+'" data-toggle="tooltip" title="'+interval.type+'"></a>';
    var o = $compile(str)($scope);
    $(o).css( "width", width + "%");
    $(o).css( "left", starting_at + "%");

    o[0].onclick = function() {
      $rootScope.$broadcast('setPeriod', interval_id, data, offset);
      o.addClass("selected");
      
      if($scope.selected != null) {
        $scope.selected.removeClass("selected");
      }
      $scope.selected = o;
    };
    
    timeline.append(o);
  };
  
  $scope.save = function(event) 
  {
    var name = $scope.widget.title.trim();
    if(name.length === 0 || name.toLowerCase() === 'new') {
      alert("ERROR: you need to set a tag.");
      return;
    }

    var url = new URL(window.location.href);
    var game = url.searchParams.get("game");
    if (game === null) {
      alert("ERROR: invalid game id.");
      return;
    }

    data = [];
    for(var i in $scope.model) {
      // TODO: clear/skip empty labels
      var str = JSON.stringify($scope.model[i].data.labels, null, '  ');
      if (str.length > 2) {
        data.push({'id':$scope.model[i].id, 'labels': str});
      }
    }
    
    $.post(null, {"tag" : $scope.widget.title, "data" : data})
      .done(function( result ) {
        console.log(result);
      });
  }
});


app.controller('FormController', function($scope) {
  
  // TODO: load those from file

  var labels = {
    "basisLabels" : {"title": "Basis", "labels": [
      {"value":"badView",       "name": "<b>view</b> obstructed"},
      {"value":"nokick",        "name": "<b>no kick motion</b> performed"},
      {"value":"delocalized",   "name": "robot <b>delocalized</b>"},
      {"value":"noBall",        "name": "<b>no ball</b> in front of robot"}
    ]},
    "situationLabels" : {"title": "Situation", "labels": [
      {"value":"moved",         "name": "ball <b>moved</b> by the kick"},
      {"value":"touch",         "name": "<b>touch</b> the ball <b>before</b> kick"},
      {"value":"pushed",        "name": "<b>pushed</b> by opponent while kicking"},
      {"value":"fall",          "name": "<b>fall</b> after kick"},
      {"value":"balldirection", "name": "ball moved in the <b>desired direction</b>"}
    ]},
    "resultLabels" : {"title": "Result", "labels": [
      {"value":"oppgoal",       "name": "<b>goal</b> scored"},
      {"value":"sideOut",       "name": "ball out on a <b>side line</b>"},
      {"value":"ownOut",        "name": "ball out on the <b>own groundline</b>"},
      {"value":"oppOut",        "name": "ball out on the <b>opponent groundline</b>"},
      {"value":"ballToOwnGoal", "name": "ball moved <b>closer to own</b> goal"},
      {"value":"ballToOppGoal", "name": "ball moved <b>closer to opponent</b> goal"}
    ]}
  };
  
  var properties = {};
  var form = [];
  
  for(var key in labels) {
    var p = labels[key];
    properties[key] = {
      "type": "array", 
      "title": p.title,
      "items": {"type": "string", "enum": p.labels.map(i => i.value)}
    };
    form.push({
      "key": key,
      "type": "checkboxes",
      "titleMap": p.labels
    });
  }
  
  properties["comment"] = {"type": "string", "title": "Comment"};
  form.push({
      "key": "comment",
      "type": "textarea",
      "placeholder": "Make a comment"
    });
  
  
  $scope.schema = {
    "type" : "object", 
    "properties": properties
  };
  
  $scope.form = form;

  $scope.model = {};
  
  /*
  $scope.onSubmit = function(form) {
  
    $scope.$broadcast('schemaFormValidate');
    
    if (form.$valid) {
      x = JSON.stringify($scope.model);
      v = 3;
      
      tmp = '{"labels":["fall after kick","touch the ball before kick","kick successful"],"comment":"ewfwefw"}';
    }
  }*/

  $scope.$on('setPeriod', function(event, interval_id, data, offset) {
      if(typeof data.labels[interval_id] === 'undefined') { data.labels[interval_id] = {}; }
      $scope.model = data.labels[interval_id];
      $scope.$apply();
  });
});


app.controller('PlayerController', function($scope) {
  $scope.$on('setPeriod', function(event, interval_id, data, offset) {
    var t_begin = data.intervals[interval_id].begin + offset;
    var t_end = data.intervals[interval_id].end + offset + (data.intervals[interval_id].type == 'none'?0.0:3.0);
    playerGlobal.setPeriod(t_begin, t_end);
  });
});

app.controller('DrawingController', function($scope) {
  $scope.$on('setPeriod', function(event, interval_id, data, offset) {
    //draw the robot position
    draw(
        data.intervals[interval_id].pose.x/10.0, 
        data.intervals[interval_id].pose.y/10.0, 
        data.intervals[interval_id].pose.r, 
        data.intervals[interval_id].ball.x/10.0, 
        data.intervals[interval_id].ball.y/10.0
    );
  });
});



app.directive('timeline', function($compile) {
  return {
    //restrict: 'AE',
    //replace: true,
    //template: '<div class="timeline"></div>',
    link: function(scope, element, attrs) {

      $.getJSON( attrs.file, function( data ) {
        // if not already available, add the label container
        if(typeof data.labels === 'undefined') { data.labels = {}; }
        if(typeof attrs.labels !== 'undefined') {
          $.getJSON( attrs.labels, function( labels ) {
            // TODO: extend instead of replace!
            data.labels = labels;
          });
        }
        // show the player number in the timeline
        element.append('<div class="info">#'+attrs.playernumber+'</div>');
        // iterate through the actions and add the interval to the timeline
        for(var interval_id in data.intervals) {
          var v = data.intervals[interval_id];
          // collect all found actions in the log file and add a control to the UI
          if($('#event_configuration input[name="'+v.type+'"]').length == 0) {
            var event_checkbox = $('<div class="col-xs-3"><div class="checkbox"><label><input type="checkbox" name="'+v.type+'" checked> '+v.type+'</label></div></div>');
            event_checkbox.change(function(e) { hide_event(e.target.name) });
            $('#event_configuration .row').append(event_checkbox);
          }
          
          scope.addPeriod(element, interval_id, data, attrs.logoffset, attrs.videooffset);
        }
        scope.addLogfileToModel(attrs.id, data);
      });
    }
  };
});

function hide_event(e) {
  $("."+e).toggleClass('visibility_hidden');
}