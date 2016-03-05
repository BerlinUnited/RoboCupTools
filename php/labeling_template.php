<!DOCTYPE html>
<html lang="en" ng-app="test">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
    
  <script src="lib/player/jquery.js"></script>
  
  <script src="lib/angular.min.js"></script>
  <script src="lib/angular-sanitize.min.js"></script>
  <script src="lib/tv4.min.js"></script>
  <script src="lib/ObjectPath.js"></script>
  
  <script src="lib/schema-form.min.js"></script>
  <script src="lib/bootstrap-decorator.js"></script>
  
  <script src="lib/player/mediaelement-and-player.min.js"></script>
  <link rel="stylesheet" href="lib/player/mediaelementplayer.css" />
  
  <link rel="stylesheet" href="lib/bootstrap/css/bootstrap.min.css" />
  <script src="lib/bootstrap/js/bootstrap.min.js"></script>
  
  <link rel="stylesheet" href="style.css" />
  <script src="js/field.js"></script>
  
  <script type="text/javascript">
  </script>
  
  <script type="text/javascript">
  
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
      
      this.currentStopListener = function() {
       if (this.currentTime > end) {
            player.setCurrentTime(start);
            this.pause();
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

  </script>
  
  <script type="text/javascript">
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
        
        var str = '<a href="#" class="'+c+'" style="width:'+width+'%" data-toggle="tooltip" title="'+data.type+'"></a>';
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
          
          $.post( "php/save.php", {"tag" : $scope.widget.title, "file": log.file, "data" : str})
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
          {"value":"delocalized",   "name": "robot is <b>delocalized</b>"},
          {"value":"noBall",        "name": "<b>no ball</b> in front of robot"},
          {"value":"badView",       "name": "<b>view</b> is obstructed"}
        ]},
        "motionLabels" : {"title": "Motion", "labels": [
          {"value":"moved",         "name": "<b>moved</b> ball by the kick"},
          {"value":"kick",          "name": "kick <b>motion</b> was performed"}
        ]},
        "situationLabels" : {"title": "Situation", "labels": [
          {"value":"pushed",        "name": "<b>pushed</b> by opponent while kicking"},
          {"value":"fall",          "name": "<b>fall</b> after kick"},
          {"value":"touch",         "name": "<b>touch</b> the ball before kick"},
          {"value":"balldirection", "name": "ball rolled in the <b>desired direction</b>"}
        ]},
        "resultLabels" : {"title": "Result", "labels": [
          {"value":"goal",          "name": "<b>goal</b> was scored"},
          {"value":"sideOut",       "name": "ball went outside on a <b>side line</b>"},
          {"value":"ownOut",        "name": "ball went outside on <b>own groundline</b>"},
          {"value":"oppOut",        "name": "ball went outside on <b>opponent groundline</b>"},
          {"value":"ballToOwnGoal", "name": "ball went <b>closer to own</b> goal"},
          {"value":"ballToOppGoal", "name": "ball went <b>closer to opponent</b> goal"}
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
        draw(data.pose.x, data.pose.y, data.pose.r, data.ball.x, data.ball.y);
      });
    });
    
    
    app.directive('timeline', function($compile) {
      return {
        restrict: 'AE',
        replace: true,
        template: '<div id="timeline" class="timeline"></div>',
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
  </script>
  
  </code>
  
</head>

<body onload="draw(0,1000,0.1, 1000, 2000);">

<div class="container-fluid" ng-controller="MainController">

  <div class="row">
    <div class="col-sm-2">
      <h3><a href="./index.php"><< BACK</a></h3>
    </div>
    <div class="col-sm-10">
      <h3><?php echo $g->name." - ".$g->half; ?></h3>
    </div>
  </div>

  <div class="row">
    
    <div class="col-sm-2">
      <div ng-controller="FormController"> 
        <form name="labels" sf-schema="schema" sf-form="form" sf-model="model" ng-submit="onSubmit(labels)"></form>
      </div>
    </div>
    
    <div class="col-sm-7">
      <div ng-controller="PlayerController">
        <video src="<?php echo $g->video_path; ?>" style="width: 100%; height: 100%;" id="player"></video>
      </div>
    </div>
    
    <div class="col-sm-3">
      <div ng-controller="DrawingController">
        <canvas id="canvas" width="7400" height="10400" style="width: 100%;"></canvas>
      </div>
    </div>
  </div>

  <div class="row">
    <div class="col-sm-12">
      <?php
      //<div data-timeline data-file="log/labels.json"></div>
        foreach ($g->logs as $key => $log) {
          echo '<div data-timeline data-file="'.$log->json[$name].'" data-logoffset="'.$log->log_offset.'" data-videooffset="'.$log->video_offset.'"></div>';
        }
      ?>
      
      <form>
        Name: <input type="text" name="lastname" data-ng-model="widget.title">
        <input type="button" value="Submit" ng-click="save($event)">
      </form>
    </div>
  </div>
  
</div>
<div style="display:none;">
  <img id="nao" src="nao.png" />
</div>

</body>
</html>