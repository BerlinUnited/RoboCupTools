<?php
/* @var $this app\View */
/* @var $half \app\models\SoccerHalftime */
/* @var $label String */
/* @var $video_file \app\models\SoccerVideo */
?>
<?php if (count($half->video) > 1) : ?>
    <div class="pull-right">
        <div class="btn-group btn-group-xs" role="group" aria-label="cameras">
            <?php
            foreach ($half->video as $key => $video) {
                echo '<a href="' . app\Url::to(['id' => $game->id, 'half' => $half->id, 'name' => $label, 'video' => $video->id]) . '" class="btn btn-default' . ($video_file == $video ? ' active' : '') . '" role="button">Cam #' . $video->camera . '</a>';
            }
            ?>
        </div>
    </div>
<?php endif; ?>