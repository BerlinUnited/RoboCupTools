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

  $scope.widget = {title: '<?php if($name != "blank") { echo $name; } ?>'};

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
  
  $scope.addLogfileToModel = function(file, data) 
  {
    $scope.model.push({"file":file, "data":data});
  }
  
  $scope.addPeriod = function(timeline, data, duration, log_offset, video_offset, duration_none, num_event) 
  {
    var offset = video_offset - log_offset;
    
    //var duration = playerGlobal.player.media.duration;
    var width = 0;
    
    var non_supression = 0.2;
    var event_duration_add = duration_none * non_supression / num_event;
    
    if(data.type == 'none') {
      width = (data.end-data.begin)/duration*(1.0 - non_supression);
    } else {
      width = (data.end-data.begin + event_duration_add)/duration;
    }
    width = Math.min(width*100, 100);
    
    var c = data.type == 'none'?'blank':'button';
    
    var str = '<a href="#" class="'+c+' '+data.type+'" style="width:'+width+'%" data-toggle="tooltip" title="'+data.type+'"></a>';
    var o = $compile(str)($scope);

    o[0].onclick = function() {
      $rootScope.$broadcast('setPeriod', data, offset);
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
    if($scope.widget.title == '') {
      alert("ERROR: you need to set a tag.");
    }
    
    //console.log($scope.widget.title);
    for(var i = 0; i < $scope.model.length; ++i) {
      var log = $scope.model[i];
      var str = JSON.stringify(log.data, null, '  ');
      //console.log(log.file);
      //console.log(str);
      //event.target.href = 'data:text/json;charset=utf8,' + encodeURIComponent(str);
      
      $.post( "php/admin/save.php", {"tag" : $scope.widget.title, "file": log.file, "data" : str})
       .done(function( result ) {
          console.log(result);
        });
    }
    //var str = JSON.stringify($scope.model, null, '  ');
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

  $scope.$on('setPeriod', function(event, data) {
      $scope.model = data.labels;
      $scope.$apply();
  });
});


app.controller('PlayerController', function($scope) {
  $scope.$on('setPeriod', function(event, data, offset) {
    var t_begin = data.begin + offset;
    var t_end = data.end + offset + (data.type == 'none'?0.0:3.0);
    playerGlobal.setPeriod(t_begin, t_end);
  });
});

app.controller('DrawingController', function($scope) {
  $scope.$on('setPeriod', function(event, data) {
    //draw the robot position
    //console.log(data.pose.x, data.pose.y, data.pose.r);
    draw(data.pose.x/10.0, data.pose.y/10.0, data.pose.r, data.ball.x/10.0, data.ball.y/10.0);
  });
});



app.directive('timeline', function($compile) {
  return {
    //restrict: 'AE',
    //replace: true,
    //template: '<div class="timeline"></div>',
    link: function(scope, element, attrs) {

      $.getJSON( attrs.file, function( data ) {
        
        // HACK: estimate the duration of the logfile
        var duration = 0;
        var num_none = 0;
        var num_event = 0;
        var duration_none = 0;
        for (var i = 0; i < data.intervals.length; i++) 
        {
          var v = data.intervals[i];
          duration = duration + (v.end-v.begin);
          
          if(v.type == 'none') {
            num_none = num_none + 1;
            duration_none = duration_none + (v.end-v.begin);
          } else {
            num_event = num_event + 1;
          }
        }
        
        for (var i = 0; i < data.intervals.length; i++) 
        {
          var v = data.intervals[i];
          if (typeof v.labels === 'undefined') {
            v.labels = {};
          }
          
          scope.addPeriod(element, v, duration, attrs.logoffset, attrs.videooffset, duration_none, num_event);
        }
        
        scope.addLogfileToModel(attrs.file, data);
      });
    }
  };
});