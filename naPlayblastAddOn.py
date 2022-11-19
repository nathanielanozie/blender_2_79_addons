#naPlayblastAddOn.py
#
#This allows playblast of certain frames in blender while filling in the gaps automatically
#it allows to work in spline yet make a playblast on two's
#
#use and modify at your own risk

#example usage it assumes first frame in list is starting frame:
#enter output image directory and number of frames to skip. click playblast button.
#
#TODO: allow more than just tiff output format
#TODO: allow custom output image prefix
#
#
#
#date last modified: 03-16-2019 added .avi writing and auto play of movie after playblast
#date last modified: 03-02-2019 initial addon release
#
#
#
#inspired by:
#Joan Marc Fuentes  https://vimeo.com/88955189
#https://stackoverflow.com/questions/14982836/rendering-and-saving-images-through-blender-python
#https://blender.stackexchange.com/questions/1101/blender-rendering-automation-build-script
#https://blender.stackexchange.com/questions/27579/render-specific-frames-with-opengl-via-python/27640
#https://stackoverflow.com/questions/27515913/create-a-copy-of-an-image-python
#https://stackoverflow.com/questions/27678156/how-to-count-by-twos-with-pythons-range
#https://stackoverflow.com/questions/3590165/join-a-list-of-items-with-different-types-as-string-in-python
#https://blenderartists.org/t/image-sequence-to-movie-using-python-script/587834/2
#https://stackoverflow.com/questions/12368568/play-quicktime-movie-from-terminal


bl_info = {
    "name":"playblast tool",
    "category": "Object"
}

import bpy

from bpy.props import(
    StringProperty,
    IntProperty,
    PointerProperty
    )

from bpy.types import(
    Operator,
    Panel,
    PropertyGroup
    )

class PlayblastOperator(Operator):
    bl_idname = "obj.do_playblast"
    bl_label = "Playblast"
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        #get directory from text field
        imgDirShort = context.scene.playblast_prop.outImgDir
        imgDir = bpy.path.abspath(imgDirShort) #because we need long directory path
        #get skip frame from text field
        skipFrameArg = context.scene.playblast_prop.numSkipFrame
        skipFrame = 1
        if skipFrameArg == 1 or skipFrameArg == 0:
            skipFrame = 1
        elif skipFrameArg > 1 and skipFrameArg <= (context.scene.frame_end-context.scene.frame_start):
            skipFrame = skipFrameArg
        else:
            self.report({'ERROR'}, "cannot find valid skip frame. check its less than total number frames")
            return {'FINISHED'}
        frames = range( context.scene.frame_start, context.scene.frame_end+1, skipFrame)
        
        self.report({'INFO'}, "Starting playblast ...")
        self.report({'INFO'}, "output dir: %s" %imgDir )
        self.report({'INFO'}, "playblasting frames: %s" %(' '.join( str(f) for f in frames )) ) #extra bit converting integer list to string
        naPlayblast( frames = frames, imageDir = imgDir, fill = True)
        self.report({'INFO'}, "Completed playblast")
        return {'FINISHED'}

class PlayblastPanel(Panel):
    bl_label = "Playblast Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    
    def draw(self, context):
        
        #here we add textfields and button to ui
        #
        layout = self.layout
        layout.label(text = "Playblast tool")
        #add image directory text field
        layout.prop( context.scene.playblast_prop, "outImgDir", text = "out image directory" )
        #add frames skip text field
        layout.prop( context.scene.playblast_prop, "numSkipFrame", text = "number of frames to skip. ex: 2 says playblast every other frame")
        layout.operator( "obj.do_playblast")

class PlayblastProperties(PropertyGroup):
    #here we make each textfield
    outImgDir = StringProperty(
        name = "imageDir",
        description = "output image directory",
        subtype = "FILE_PATH"
        )

    numSkipFrame = IntProperty(
        name = "numSkipFrame",
        description = "number of frames to skip. ex: 2 means playblast every other frame"
        )

def register():
    bpy.utils.register_class(PlayblastOperator)
    bpy.utils.register_class(PlayblastPanel)
    bpy.utils.register_class(PlayblastProperties)
    #here we name the property that holds all our textfields
    bpy.types.Scene.playblast_prop = PointerProperty(
        type = PlayblastProperties
        )
    
def unregister():
    bpy.utils.unregister_class(PlayblastOperator)
    bpy.utils.unregister_class(PlayblastPanel)
    bpy.utils.unregister_class(PlayblastProperties)
    del bpy.types.Scene.playblast_prop
    
if __name__ == "__main__":
    register()


##############actual playblast code
import shutil
import os
import bpy

def naPlayblast( frames = [1,3,5], imageDir = "/Users/Nathaniel/Desktop/SINGLE_BLENDER_FACE_RIG/intro_blender_pipe/output/tmpPlayblast", fill = True):
    """
    list of frames
    output image directory
    fill False means only playblast skip frames and dont fill in missing frames
    """
    if not os.path.exists( imageDir ):
        print('cannot find output directory')
        return
    
    if frames[0] != bpy.context.scene.frame_start:
        print('only works with starting frame given matches with timeline')
        return
    
    setImageExt()
    #playblast chosen frames
    for frame in frames:
        bpy.context.scene.frame_set(frame)
        imageName = getImageNameFromNumber(frame)
        imagePath = os.path.join( imageDir, imageName )
        bpy.data.scenes["Scene"].render.filepath = imagePath
        bpy.ops.render.opengl(write_still=True)
    
    #fill in missing frames
    if fill:
        missingInfoDict = getFillMissingFramesDictionary( frames )
        fillMissingFrames( missingInfoDict, imageDir )
    #done wrting images

    #write movie file
    movieName = 'anim.avi'
    convertImgToVideo( inputDir = imageDir, \
                        outputDir = imageDir, \
                        outputFileName = movieName,\
                        outputFormat = 'AVI_JPEG',\
                        resolutionX = 720,\
                        resolutionY = 480
                        )
    
    #play movie
    playMovie( movie = os.path.join(imageDir,movieName) )


def setImageExt():
    """can change this for different image extension
    """
    bpy.context.scene.render.image_settings.file_format = 'TIFF'
def getImageExt():
    return 'tif'
    
def getImageNameFromNumber( frame = 1 ):
    """can change this to any image name formatting
    """
    return 'img_%d.%s' %(frame, getImageExt() )
    
def getFillMissingFramesDictionary( sourceFrames = [1,3,5] ):
    """keys are source image name values list of destination image names needed to fill
    #this gives info for filling in images
    #ex result given [1,3,5] it assumes always beginning with start frame:  
    #{ 'img_1':['img_2'], 'img_3':[img_4] }
    """
    startFrame = bpy.context.scene.frame_start
    endFrame = bpy.context.scene.frame_end
    if sourceFrames[0] != startFrame:
        print( 'cannot handle source frames not starting at %d.' %startFrame)
        return
        
    result = {}
    for i in range(0,len(sourceFrames)-1):
        #print sourceFrames[i], range( sourceFrames[i]+1, sourceFrames[i+1] )
        sImage = getImageNameFromNumber( sourceFrames[i] )
        dImages = [ getImageNameFromNumber(x) for x in range( sourceFrames[i]+1, sourceFrames[i+1] ) ] 
        result[ sImage ] = dImages
    
    #fill in up to total frames if needed
    if sourceFrames[ len(sourceFrames) - 1 ] != endFrame:
        sImage = getImageNameFromNumber( sourceFrames[len(sourceFrames)-1] )
        dImages = [ getImageNameFromNumber(x) for x in range( sourceFrames[ len(sourceFrames)-1 ]+1, endFrame+1 ) ]     
        result[ sImage ] = dImages
    return result
    

def fillMissingFrames( imgDict = { 'img_1':['img_2'], 'img_3':['img_4'] }, imgDir = '/Users/Nathaniel/Desktop/SINGLE_BLENDER_FACE_RIG/intro_blender_pipe/output/tmpPlayblast' ):
    """
    this does actual copy of images
    #given ex: { 'img_1':['img_2'], 'img_3':[img_4] }, imgDir = '/Users/Nathaniel/Desktop/SINGLE_BLENDER_FACE_RIG/intro_blender_pipe/output/tmpPlayblast' 
    """
    for sourceImage in imgDict.keys():
        destinationImages = imgDict[sourceImage]
        for dImage in destinationImages:
            dImageFull = os.path.join( imgDir, dImage )
            sImageFull = os.path.join( imgDir, sourceImage )
            if not os.path.exists( sImageFull ):
                print('could not find source image %s, skipping' %sImageFull)
                continue
            shutil.copy( sImageFull, dImageFull )
            
#work on movie writing
def convertImgToVideo(
    inputDir = '/Users/Nathaniel/Desktop/SINGLE_BLENDER_FACE_RIG/intro_blender_pipe/output/tmpPlayblast', \
    inputImageExt = 'tif',\
    outputDir = '/Users/Nathaniel/Desktop/SINGLE_BLENDER_FACE_RIG/intro_blender_pipe/output/tmpPlayblast', \
    outputFileName = 'test.avi', \
    outputFormat = 'AVI_JPEG', \
    resolutionX = 720 ,\
    resolutionY = 480 
    ):
    """
    convert images in folder to video using blender
    #other res example 1920x1080
    """
    
    #set scene settings
    bpy.data.scenes["Scene"].render.resolution_x = resolutionX
    bpy.data.scenes["Scene"].render.resolution_y = resolutionY
    bpy.data.scenes["Scene"].render.resolution_percentage = 100

    #get input images from directory
    unsortedInputImages = [ path for path in os.listdir(inputDir) if os.path.splitext(path)[1].endswith(inputImageExt) ]
    
    #sort input images
    inputImages = []
    tempDict = {}
    for img in unsortedInputImages:
        tempDict[ int( (img.split('.')[0]).split('_')[1] ) ] = img
    for k,v in sorted( tempDict.items() ):
        inputImages.append( v )
    
    #use blender sequencer
    inputFiles = [ {"name":i} for i in inputImages ]
    print(inputFiles)
    numFrames = len(inputFiles)
    
    area = bpy.context.area
    old_type = area.type
    area.type = 'SEQUENCE_EDITOR'
    strip_obj = bpy.ops.sequencer.image_strip_add(directory = inputDir, files = inputFiles, channel = 1, frame_start=0, frame_end = numFrames-1 )
    area.type = old_type
    
    bpy.data.scenes["Scene"].frame_end = numFrames
    bpy.data.scenes["Scene"].render.image_settings.file_format = outputFormat
    bpy.data.scenes["Scene"].render.filepath = os.path.join(outputDir,outputFileName)
    bpy.ops.render.render(animation = True)
    
    #clean up
    bpy.ops.sequencer.delete()


def playMovie(movie = '/Users/Nathaniel/Desktop/SINGLE_BLENDER_FACE_RIG/intro_blender_pipe/output/tmpPlayblast/test.avi'):
    if not os.path.exists(movie):
        print('no movie found to play')
        return
    os.system( 'open ' + movie )



