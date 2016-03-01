<?php
  include 'php/listcontents.php';
  
  $game = NULL;
  
  foreach ($games as $key => $g) {
		if(sizeof($g->logs) > 0) {
			
      /*
			echo '<div><a href="'.$g->video_path.'">'.$g->name.' - '.$g->half.'</a>';
			
			foreach ($g->logs as $key => $log) {
				echo '<div><a href="'.$log->json.'">'.$g->name.'</a></div>';
			}
			
			echo '</div>';
      */
      $game = $g;
      break;
		}
	}
?>

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
    
      $scope.model = {};
      $scope.selected = null;
    
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
      
      $scope.addPeriod = function(timeline, data, duration, log_offset, video_offset) 
      {
        var offset = video_offset - log_offset;
        
        //var duration = playerGlobal.player.media.duration;
        var width = Math.min((data.end-data.begin)/duration*100, 100);
        
        var str = '<a href="#" class="'+data.type+'" style="width:'+width+'%" data-toggle="tooltip" title="'+data.label+'"></a>';
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
      
      $scope.save = function(event) {
        var str = JSON.stringify($scope.model, null, '  ');
        console.log(str);
        event.target.href = 'data:text/json;charset=utf8,' + encodeURIComponent(str);
      }
    });
    
    
    app.controller('FormController', function($scope) {
      
      // TODO: load those from file
      var labelMap = [
        {"value":"pushed",   "name": "<b>pushed</b> by opponent while kicking"},
        {"value":"fall",     "name": "<b>fall</b> after kick"},
        {"value":"ballmiss", "name": "kick empty space just after ball has left"},
        {"value":"touch",    "name": "<b>touch</b> the ball before kick"},
        {"value":"moved",    "name": "<b>moved</b> ball by the kick"},
        {"value":"miss",     "name": "ball was <b>not moved</b> by the kick"},
        {"value":"ghost",    "name": "empty space kick"}
      ];
      
      var myTitle = "Labels for different kick actions";
      
      
      $scope.schema = {
        "type" : "object", 
        "properties": {
          "labels": {
            "type": "array", 
            "title": myTitle,
            "items": {"type": "string", "enum": labelMap.map(i => i.value)}
          },
          "comment": {"type": "string", "title": "Comment"}
        }
      };
      
      $scope.form = [
        {
          "key": "labels",
          "type": "checkboxes",
          "titleMap": labelMap
        },
        {
          "key": "comment",
          "type": "textarea",
          "placeholder": "Make a comment"
        }
      ];

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
        
        playerGlobal.setPeriod(data.begin + offset, data.end + offset);

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
            for (var i = 0; i < data.intervals.length; i++) 
            {
              var v = data.intervals[i];
              duration = duration + (v.end-v.begin);
            }
            
            for (var i = 0; i < data.intervals.length; i++) 
            {
              var v = data.intervals[i];
              if (typeof v.labels === 'undefined') {
                v.labels = {};
              }
              
              scope.addPeriod(element, v, duration, attrs.logoffset, attrs.videooffset);
              scope.model = data;
            }
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
      <div ng-controller="FormController"> 
        <form name="labels" sf-schema="schema" sf-form="form" sf-model="model" ng-submit="onSubmit(labels)"></form>
      </div>
    </div>
    
    <div class="col-sm-7">
      <div ng-controller="PlayerController">
        <video src="<?php echo $g->video_path; ?>" width="640" height="480" style="width: 100%; height: 100%;" id="player"></video>
      </div>
    </div>
    
    <div class="col-sm-3">
      <div ng-controller="DrawingController">
        <canvas id="canvas" width="7400" height="10400" style="width: 100%; height: 100%;"></canvas>
      </div>
    </div>
  </div>

  <div class="row">
    <div class="col-sm-12">
      <?php
      //<div data-timeline data-file="log/labels.json"></div>
        foreach ($g->logs as $key => $log) {
          echo '<div data-timeline data-file="'.$log->json.'" data-logoffset="'.$log->log_offset.'" data-videooffset="'.$log->video_offset.'"></div>';
        }
      ?>
      <a ng-click="save($event)" download="labels.json" href="#">Export</a>
    </div>
  </div>
  
</div>
<div style="display:none;">
  <img id="nao" src="nao.png" />
</div>

</body>
</html>