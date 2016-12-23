<?php
/* @var $this app\View */
/* @var $game \app\models\SoccerGame */
/* @var $half \app\models\SoccerHalftime */
/* @var $label String */
/* @var $video String */

$this->title = \app\Application::$app->name . ' ::: ' . \app\Application::$app->params['ownTeamName'] .' vs. '. $game->getOpponent();

$this->registerCssFile('lib/player/mediaelementplayer.css');
$this->registerCssFile('style.css');

$this->registerJsFile('lib/angular.min.js');
$this->registerJsFile('lib/angular-sanitize.min.js');
$this->registerJsFile('lib/tv4.min.js');
$this->registerJsFile('lib/ObjectPath.js');
$this->registerJsFile('lib/schema-form.min.js');
$this->registerJsFile('lib/bootstrap-decorator.js');
$this->registerJsFile('lib/player/mediaelement-and-player.min.js');
$this->registerJsFile('js/field.js');
// TODO: move JS to own/seperate file!
$this->registerJs('
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
    $("#player").mediaelementplayer({
      success: function(media, node, player) {
        $("#" + node.id + "-mode").html("mode: " + player.pluginType);
        
        media.addEventListener("loadedmetadata", function() {
          playerGlobal = new PeriodicPlayer(player);
        });
      }
    });
  });');

$js =<<<'JS'
    var app = angular.module('test', ['schemaForm']);
    
    app.controller('MainController', function($rootScope, $scope, $compile) {
    
      $scope.model = [];
      $scope.selected = null;
    
      $scope.widget = {title: '%title%'};
    
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
          $("#labelset-name").parent().addClass("has-error");
          alert("ERROR: you need to set a tag.");
          return;
        } else {
          $("#labelset-name").parent().removeClass("has-error");
          $("#labelset-name").parent().addClass("has-success");
        }
        var error_box = $("form[name='label-form']").find(".alert");
        
        //console.log($scope.widget.title);
        for(var i = 0; i < $scope.model.length; ++i) {
          var log = $scope.model[i];
          var str = JSON.stringify(log.data, null, '  ');
          //console.log(log.file);
          //console.log(str);
          //event.target.href = 'data:text/json;charset=utf8,' + encodeURIComponent(str);
          
          $.post( "%save%", {"tag" : $scope.widget.title, "file": log.file, "data" : str})
           .done(function( result ) {
              console.log(result);
              if(!error_box.hasClass("hidden")) {
                error_box.addClass("hidden");
              }
            }).fail(function(qXHR, textStatus, errorThrown) {
              error_box.html("<strong>ERROR: "+qXHR.statusText+"</strong>"+qXHR.responseText);
              error_box.removeClass("hidden");
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
JS;
$search = ['%title%', '%save%'];
$replace = ['',\app\Url::to(['save'])];
$this->registerJs(str_replace($search, $replace, $js));
$this->registerJs('draw(0,100,0.1, 100, 200);', app\View::POS_READY);
$this->registerCss('
    .labels a {
        margin: 5px;
    }
    .labels {
        margin-bottom:5px;
    }
');
// determine video for this halftime
$video_file = $video === NULL ? $half->getFirstVideo() : $half->getVideoById($video);
?>
<div class="row">
    <div class="col-xs-2">
        <h3><a href="<?= \app\Url::home() ?>"><<&nbsp;BACK</a></h3>
    </div>
    <div class="col-xs-10">
        <h3><?=\app\Application::$app->params['ownTeamName']?> vs. <?= $game->getOpponent()?>, <?=$half->id?>. half <small>(<?=$game->getEvent()?>, <?=$game->getDate()?>)</small></h3>
    </div>
</div>

<div class="row">
    <!-- Video & Timeline -->
    <div class="col-xs-12 col-sm-8 col-lg-7 col-lg-push-2">
        <div class="row">
            <div class="col-xs-12">
                <?=$this->render('camera_buttons', ['game'=>$game,'half'=>$half, 'label'=>$label, 'video_file'=>$video_file])?>
            </div>
            <div class="col-xs-12">
                <div ng-controller="PlayerController">
                    <video style="width: 100%; height: 100%;" id="player">
                    <?php
                        // TODO: different resolutions|formats should be here! (not half times)
                        echo implode("\n",array_map(function($f){ return '<source src="'.$f.'">'; }, $video_file->getFiles()));
                    ?>
                    </video>
                </div>
            </div>
            <div class="col-xs-12">
                <?php
                foreach ($half->robots as $log) {
                    echo '<div data-timeline data-file="' . $log->getLabelFile($label) . '" data-logoffset="' . $log->log_offset . '" data-videooffset="' . $log->video_offset . '"></div>';
                }
                ?>
            </div>
        </div>
    </div>
    
    <!-- Soccer field -->
    <div class="col-xs-6 col-sm-4 col-lg-3 col-lg-push-2">
        <div ng-controller="DrawingController">
            <canvas id="canvas" width="740" height="1040" style="width: 100%;"></canvas>
        </div>
    </div>
    
    <!-- comment & labeling -->
    <div class="col-xs-6 col-sm-12 col-lg-2 col-lg-pull-10">
        <div ng-controller="FormController"> 
            <form name="labels" sf-schema="schema" sf-form="form" sf-model="model" ng-submit="onSubmit(labels)"></form>
        </div>
        
        <hr>
        
        <form name="label-form">
            <div class="form-group">
                <label class="control-label" for="labelset-name">Label set:</label>
                <input type="text" name="labelset-name" data-ng-model="widget.title" class="form-control" id="labelset-name" placeholder="Name of the new label set">
            </div>
            <div class="form-group">
                <button type="button" ng-click="save($event)" class="btn btn-primary btn-block">Submit</button>
            </div>
            <div class="alert alert-danger hidden" role="alert">An error occurred!</div>
        </form>
    </div>
</div>

<div style="display:none;">
  <img id="nao" src="nao.png" />
</div>
