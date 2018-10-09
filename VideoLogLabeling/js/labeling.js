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
      showSavingAlert('<b>WARNING: you need to set a tag!</b>', 'alert alert-warning', 1000, true);
      return;
    }

    var url = new URL(window.location.href);
    var game = url.searchParams.get("game");
    if (game === null) {
      showSavingAlert('<b>ERROR: invalid game id!</b>', 'alert alert-danger', 0, false);
      return;
    }

    data = [];
    for(var i in $scope.model) {
      // check & remove empty objects/arrays
      var lbl = $scope.model[i].data.labels;
      for(var l in lbl) {
        for(var a in lbl[l]) {
          if ($.isEmptyObject(lbl[l][a])) { delete lbl[l][a]; }
        }
        if ($.isEmptyObject(lbl[l])) { delete lbl[l]; }
      }
      if ($.isEmptyObject(lbl)) { continue; }
      // add to the sending array
      data.push({'id':$scope.model[i].id, 'labels': JSON.stringify($scope.model[i].data.labels, null, '  ')});
    }

    if(data.length > 0) {
      $.post(null, {"tag" : $scope.widget.title, "data" : data})
        .done(function( result ) {
          if (result === 'SUCCESS') {
            showSavingAlert('<b>Saved!</b>', 'alert alert-success', 800, true);
          } else {
            showSavingAlert('<b>'+result+'</b>', 'alert alert-danger', 0, false);
          }
        });
    } else {
      showSavingAlert('<b>Nothing to save!</b>', 'alert alert-warning', 600, true);
    }
  }
});


app.controller('FormController', function($scope) {
  labels = typeof ANNOTATION_LABELS === 'undefined' ? {} : ANNOTATION_LABELS;
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
    var t_begin = data.intervals[interval_id].begin + offset - 3.0;
    var t_end = data.intervals[interval_id].end + offset + 3.0;
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
            $.extend(data.labels, labels);
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

function showSavingAlert(content, clz, delay, fadeout) {
  var alert = $("#label_title_form .alert");
  alert.html(content).attr('class', clz).fadeIn();
  if (fadeout) {
    alert.delay(delay).fadeOut();
  }
}

// initialize the alert
$("#label_title_form .alert").hide();
$("#label_title_form .alert").removeClass('hidden');
