# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DsgTools
                                 A QGIS plugin
 Brazilian Army Cartographic Production Tools
                              -------------------
        begin                : 2018-08-15
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Philipe Borba - Cartographic Engineer @ Brazilian Army
        email                : borba.philipe@eb.mil.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import uuid

import processing
from qgis.core import Qgis, QgsProcessingUtils, QgsProcessingFeatureSourceDefinition


class AlgRunner:
    (
        Break,
        Snap,
        RmDangle,
        ChDangle,
        RmBridge,
        ChBridge,
        RmDupl,
        RmDac,
        BPol,
        Prune,
        RmArea,
        RmLine,
        RMSA,
    ) = range(13)

    def generateGrassOutputAndError(self):
        uuid_value = str(uuid.uuid4()).replace("-", "")
        output = QgsProcessingUtils.generateTempFilename(
            "output_{uuid}.shp".format(uuid=uuid_value)
        )
        error = QgsProcessingUtils.generateTempFilename(
            "error_{uuid}.shp".format(uuid=uuid_value)
        )
        return output, error

    def getGrassReturn(self, outputDict, context, returnError=False):
        lyr = QgsProcessingUtils.mapLayerFromString(outputDict["output"], context)
        if returnError:
            errorLyr = QgsProcessingUtils.mapLayerFromString(
                outputDict["error"], context
            )
            return lyr, errorLyr
        else:
            return lyr

    def runDissolve(
        self,
        inputLyr,
        context,
        feedback=None,
        outputLyr=None,
        field=None,
        is_child_algorithm=False,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        field = [] if field is None else field
        parameters = {"INPUT": inputLyr, "FIELD": field, "OUTPUT": outputLyr}
        output = processing.run(
            "native:dissolve",
            parameters,
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runGrassDissolve(
        self,
        inputLyr,
        context,
        feedback=None,
        column=None,
        outputLyr=None,
        onFinish=None,
    ):
        """
        Runs dissolve from GRASS algorithm provider.
        :param inputLyr: (QgsVectorLayer) layer to be dissolved.
        :param context: (QgsProcessingContext) processing context.
        :param feedback: (QgsProcessingFeedback) QGIS object to keep track of progress/cancelling option.
        :param column: ()
        :param outputLyr: (str) URI to output layer.
        :param onFinish: (list-of-str) sequence of algs to be run after dissolve is executed, in execution order.
        :return: (QgsVectorLayer) dissolved (output) layer.
        """
        parameters = {
            "GRASS_MIN_AREA_PARAMETER": 0.0001,
            "GRASS_OUTPUT_TYPE_PARAMETER": 0,
            "GRASS_REGION_PARAMETER": None,
            "GRASS_SNAP_TOLERANCE_PARAMETER": -1,
            "GRASS_VECTOR_DSCO": "",
            "GRASS_VECTOR_EXPORT_NOCAT": False,
            "GRASS_VECTOR_LCO": "",
            "column": column,
            "input": inputLyr,
            "output": outputLyr
            or QgsProcessingUtils.generateTempFilename("output.shp"),
        }
        output = processing.run(
            "grass7:v.dissolve", parameters, onFinish, feedback, context
        )
        return self.getGrassReturn(output, context)

    def runDonutHoleExtractor(
        self,
        inputLyr,
        context,
        feedback=None,
        donuthole=None,
        outershell=None,
        selected=False,
    ):
        donuthole = "memory:" if donuthole is None else donuthole
        outershell = "memory:" if outershell is None else outershell
        parameters = {
            "INPUT": inputLyr,
            "SELECTED": selected,
            "OUTERSHELL": outershell,
            "DONUTHOLE": donuthole,
        }
        output = processing.run(
            "dsgtools:donutholeextractor",
            parameters,
            context=context,
            feedback=feedback,
        )
        return output["OUTERSHELL"], output["DONUTHOLE"]

    def runDeleteHoles(
        self, inputLyr, context, feedback=None, outputLyr=None, min_area=0
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"INPUT": inputLyr, "MIN_AREA": min_area, "OUTPUT": outputLyr}
        output = processing.run(
            "native:deleteholes", parameters, context=context, feedback=feedback
        )
        return output["OUTPUT"]

    def runOverlay(
        self,
        lyrA,
        lyrB,
        context,
        atype=0,
        btype=0,
        feedback=None,
        snap=0,
        operator=0,
        minArea=1e-8,
    ):
        output, _ = self.generateGrassOutputAndError()
        parameters = {
            "ainput": lyrA,
            "atype": atype,
            "binput": lyrB,
            "btype": btype,
            "operator": operator,
            "snap": snap,
            "-t": False,
            "output": output,
            "GRASS_REGION_PARAMETER": None,
            "GRASS_SNAP_TOLERANCE_PARAMETER": -1,
            "GRASS_MIN_AREA_PARAMETER": minArea,
            "GRASS_OUTPUT_TYPE_PARAMETER": 0,
            "GRASS_VECTOR_DSCO": "",
            "GRASS_VECTOR_LCO": "",
        }
        outputDict = processing.run(
            "grass7:v.overlay", parameters, context=context, feedback=feedback
        )
        return self.getGrassReturn(outputDict, context)

    def runClean(
        self,
        inputLyr,
        toolList,
        context,
        feedback=None,
        typeList=None,
        returnError=False,
        useFollowup=False,
        snap=None,
        minArea=None,
    ):
        snap = -1 if snap is None else snap
        minArea = 0.0001 if minArea is None else minArea
        typeList = [0, 1, 2, 3, 4, 5, 6] if typeList is None else typeList
        output, error = self.generateGrassOutputAndError()
        parameters = {
            "input": inputLyr,
            "type": typeList,
            "tool": toolList,
            "-b": False,
            "-c": useFollowup,
            "output": output,
            "error": error,
            "GRASS_REGION_PARAMETER": None,
            "GRASS_SNAP_TOLERANCE_PARAMETER": snap,
            "GRASS_MIN_AREA_PARAMETER": minArea,
            "GRASS_OUTPUT_TYPE_PARAMETER": 0,
            "GRASS_VECTOR_DSCO": "",
            "GRASS_VECTOR_LCO": "",
            "GRASS_VECTOR_EXPORT_NOCAT": False,
        }
        outputDict = processing.run(
            "grass7:v.clean", parameters, context=context, feedback=feedback
        )
        return self.getGrassReturn(outputDict, context, returnError=returnError)

    def runDsgToolsClean(
        self,
        inputLyr,
        context,
        feedback=None,
        onlySelected=False,
        snap=None,
        minArea=None,
        flags=None,
    ):
        snap = -1 if snap is None else snap
        minArea = 0.0001 if minArea is None else minArea
        flags = "memory:" if flags is None else flags
        parameters = {
            "INPUT": inputLyr,
            "SELECTED": onlySelected,
            "TOLERANCE": snap,
            "MINAREA": minArea,
            "FLAGS": flags,
        }
        output = processing.run(
            "dsgtools:cleangeometries", parameters, context=context, feedback=feedback
        )
        return output["OUTPUT"]

    def runDouglasSimplification(
        self,
        inputLyr,
        threshold,
        context,
        feedback=None,
        snap=None,
        minArea=None,
        iterations=None,
        type=None,
        returnError=False,
        flags=None,
    ):
        """
        Runs simplify GRASS algorithm
        :param inputLyr: (QgsVectorLayer) layer, or layers, to be dissolved.
        :param method: (QgsProcessingParameterEnum) which algorithm would be
            used to simplify lines, in this case, Douglas-Peucker Algorithm.
        :param threshold: (QgsProcessingParameterNumber) give in map units.
            For latitude-longitude locations give in decimal degree.
        :param context: (QgsProcessingContext) processing context.
        :param feedback: (QgsProcessingFeedback) QGIS object to keep track of
            progress/cancelling option.
        :param onlySelected: (QgsProcessingParameterBoolean) process only
            selected features.
        :param outputLyr: (str) URI to output layer.
        :return: (QgsVectorLayer) simplified output layer or layers.
        """
        snap = -1 if snap is None else snap
        minArea = 0.0001 if minArea is None else minArea
        iterations = 1 if iterations is None else iterations
        flags = "memory:" if flags is None else flags
        algType = [0, 1, 2] if type is None else type
        output, error = self.generateGrassOutputAndError()
        parameters = {
            "input": inputLyr,
            "type": algType,
            "cats": "",
            "where": "",
            "method": 0,
            "threshold": threshold,
            "look_ahead": 7,
            "reduction": 50,
            "slide": 0.5,
            "angle_thresh": 3,
            "degree_thresh": 0,
            "closeness_thresh": 0,
            "betweeness_thresh": 0,
            "alpha": 1,
            "beta": 1,
            "iterations": iterations,
            "-t": False,
            "-l": True,
            "output": output,
            "error": error,
            "GRASS_REGION_PARAMETER": None,
            "GRASS_SNAP_TOLERANCE_PARAMETER": snap,
            "GRASS_MIN_AREA_PARAMETER": minArea,
            "GRASS_OUTPUT_TYPE_PARAMETER": 0,
            "GRASS_VECTOR_DSCO": "",
            "GRASS_VECTOR_LCO": "",
        }
        outputDict = processing.run(
            "grass7:v.generalize", parameters, context=context, feedback=feedback
        )
        return self.getGrassReturn(outputDict, context, returnError=returnError)

    def runIdentifyDuplicatedGeometries(
        self, inputLyr, context, feedback=None, flagLyr=None, onlySelected=False
    ):
        flagLyr = "memory:" if flagLyr is None else flagLyr
        parameters = {"INPUT": inputLyr, "SELECTED": onlySelected, "FLAGS": flagLyr}
        output = processing.run(
            "dsgtools:identifyduplicatedgeometries",
            parameters,
            context=context,
            feedback=feedback,
        )
        return output["FLAGS"]

    def runIdentifyDuplicatedFeatures(
        self,
        inputLyr,
        context,
        onlySelected=False,
        attributeBlackList=None,
        excludePrimaryKeys=True,
        ignoreVirtualFields=True,
        feedback=None,
        flagLyr=None,
    ):
        flagLyr = "memory:" if flagLyr is None else flagLyr
        attributeBlackList = [] if attributeBlackList is None else attributeBlackList
        parameters = {
            "INPUT": inputLyr,
            "SELECTED": onlySelected,
            "FLAGS": flagLyr,
            "ATTRIBUTE_BLACK_LIST": attributeBlackList,
            "IGNORE_VIRTUAL_FIELDS": ignoreVirtualFields,
            "IGNORE_PK_FIELDS": excludePrimaryKeys,
        }
        output = processing.run(
            "dsgtools:identifyduplicatedfeatures",
            parameters,
            context=context,
            feedback=feedback,
        )
        return output["FLAGS"]

    def runIdentifySmallLines(
        self, inputLyr, tol, context, feedback=None, flagLyr=None, onlySelected=False
    ):
        flagLyr = "memory:" if flagLyr is None else flagLyr
        parameters = {
            "INPUT": inputLyr,
            "TOLERANCE": tol,
            "SELECTED": onlySelected,
            "FLAGS": flagLyr,
        }
        output = processing.run(
            "dsgtools:identifysmalllines",
            parameters,
            context=context,
            feedback=feedback,
        )
        return output["FLAGS"]

    def runIdentifySmallPolygons(
        self, inputLyr, tol, context, feedback=None, flagLyr=None, onlySelected=False
    ):
        flagLyr = "memory:" if flagLyr is None else flagLyr
        parameters = {
            "INPUT": inputLyr,
            "TOLERANCE": tol,
            "SELECTED": onlySelected,
            "FLAGS": flagLyr,
        }
        output = processing.run(
            "dsgtools:identifysmallpolygons",
            parameters,
            context=context,
            feedback=feedback,
        )
        return output["FLAGS"]

    def runSnapGeometriesToLayer(
        self,
        inputLayer,
        referenceLayer,
        tol,
        context,
        feedback=None,
        behavior=None,
        outputLyr=None,
        is_child_algorithm=False,
    ):
        behavior = 0 if behavior is None else behavior
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {
            "INPUT": inputLayer,
            "REFERENCE_LAYER": referenceLayer,
            "TOLERANCE": tol,
            "BEHAVIOR": behavior,
            "OUTPUT": outputLyr,
        }
        output = processing.run(
            "qgis:snapgeometries",
            parameters,
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runSnapLayerOnLayer(
        self,
        inputLayer,
        referenceLayer,
        tol,
        context,
        onlySelected=False,
        feedback=None,
        behavior=None,
        buildCache=False,
        is_child_algorithm=False,
    ):
        behavior = 0 if behavior is None else behavior
        parameters = {
            "INPUT": inputLayer,
            "SELECTED": onlySelected,
            "REFERENCE_LAYER": referenceLayer,
            "TOLERANCE": tol,
            "BEHAVIOR": behavior,
            "BUILD_CACHE": buildCache,
        }
        output = processing.run(
            "dsgtools:snaplayeronlayer",
            parameters,
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runIdentifyDangles(
        self,
        inputLayer,
        searchRadius,
        context,
        feedback=None,
        onlySelected=False,
        lineFilter=None,
        polygonFilter=None,
        ignoreDanglesOnUnsegmentedLines=False,
        inputIsBoundaryLayer=False,
        geographicBoundsLyr=None,
        flagLyr=None,
        returnProcessingDict=False,
    ):
        flagLyr = "memory:" if flagLyr is None else flagLyr
        lineFilter = [] if lineFilter is None else lineFilter
        polygonFilter = [] if polygonFilter is None else polygonFilter
        parameters = {
            "INPUT": inputLayer,
            "SELECTED": onlySelected,
            "TOLERANCE": searchRadius,
            "LINEFILTERLAYERS": lineFilter,
            "POLYGONFILTERLAYERS": polygonFilter,
            "IGNORE_DANGLES_ON_UNSEGMENTED_LINES": ignoreDanglesOnUnsegmentedLines,
            "INPUT_IS_BOUDARY_LAYER": inputIsBoundaryLayer,
            "GEOGRAPHIC_BOUNDARY": geographicBoundsLyr,
            "FLAGS": flagLyr,
        }
        output = processing.run(
            "dsgtools:identifydangles", parameters, context=context, feedback=feedback
        )
        return output if returnProcessingDict else output["FLAGS"]

    def runSnapToGrid(self, inputLayer, tol, context, feedback=None, outputLyr=None):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {
            "INPUT": inputLayer,
            "HSPACING": tol,
            "VSPACING": tol,
            "ZSPACING": 0,
            "MSPACING": 0,
            "OUTPUT": outputLyr,
        }
        output = processing.run(
            "native:snappointstogrid", parameters, context=context, feedback=feedback
        )
        return output["OUTPUT"]

    def runRemoveNull(self, inputLayer, context, feedback=None, outputLyr=None):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"INPUT": inputLayer, "OUTPUT": outputLyr}
        output = processing.run(
            "native:removenullgeometries",
            parameters,
            context=context,
            feedback=feedback,
        )
        return output["OUTPUT"]

    def runClip(
        self,
        inputLayer,
        overlayLayer,
        context,
        feedback=None,
        outputLyr=None,
        is_child_algorithm=False,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"INPUT": inputLayer, "OVERLAY": overlayLayer, "OUTPUT": outputLyr}
        output = processing.run(
            "native:clip",
            parameters,
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runSymDiff(
        self, inputLayer, overlayLayer, context, feedback=None, outputLyr=None
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"INPUT": inputLayer, "OVERLAY": overlayLayer, "OUTPUT": outputLyr}
        output = processing.run(
            "native:symmetricaldifference",
            parameters,
            context=context,
            feedback=feedback,
        )
        return output["OUTPUT"]

    def runBoundary(self, inputLayer, context, feedback=None, outputLyr=None):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"INPUT": inputLayer, "OUTPUT": outputLyr}
        output = processing.run(
            "native:boundary", parameters, context=context, feedback=feedback
        )
        return output["OUTPUT"]

    def runMultipartToSingleParts(
        self,
        inputLayer,
        context,
        feedback=None,
        outputLyr=None,
        is_child_algorithm=False,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"INPUT": inputLayer, "OUTPUT": outputLyr}
        output = processing.run(
            "native:multiparttosingleparts",
            parameters,
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runBuffer(
        self,
        inputLayer,
        distance,
        context,
        dissolve=False,
        endCapStyle=None,
        joinStyle=None,
        segments=None,
        mitterLimit=None,
        feedback=None,
        outputLyr=None,
        is_child_algorithm=False,
    ):
        endCapStyle = 0 if endCapStyle is None else endCapStyle
        joinStyle = 0 if joinStyle is None else joinStyle
        segments = 5 if segments is None else segments
        mitterLimit = 2 if mitterLimit is None else mitterLimit
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {
            "INPUT": inputLayer,
            "DISTANCE": distance,
            "DISSOLVE": dissolve,
            "END_CAP_STYLE": endCapStyle,
            "JOIN_STYLE": endCapStyle,
            "SEGMENTS": segments,
            "MITER_LIMIT": mitterLimit,
            "OUTPUT": outputLyr,
        }
        output = processing.run(
            "native:buffer",
            parameters,
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runIntersection(
        self,
        inputLyr,
        context,
        inputFields=None,
        outputLyr=None,
        overlayLyr=None,
        overlayFields=None,
        feedback=None,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        inputFields = [] if inputFields is None else inputFields
        overlayFields = [] if overlayFields is None else overlayFields
        parameters = {
            "INPUT": inputLyr,
            "INPUT_FIELDS": inputFields,
            "OUTPUT": outputLyr,
            "OVERLAY": overlayLyr,
            "OVERLAY_FIELDS": overlayFields,
        }
        output = processing.run(
            "native:intersection", parameters, context=context, feedback=feedback
        )
        return output["OUTPUT"]

    def runFilterExpression(
        self, inputLyr, expression, context, outputLyr=None, feedback=None
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"EXPRESSION": expression, "INPUT": inputLyr, "OUTPUT": outputLyr}
        output = processing.run(
            "native:extractbyexpression", parameters, context=context, feedback=feedback
        )
        return output["OUTPUT"]

    def runRemoveDuplicatedFeatures(
        self,
        inputLyr,
        context,
        onlySelected=False,
        attributeBlackList=None,
        excludePrimaryKeys=True,
        ignoreVirtualFields=True,
        feedback=None,
        outputLyr=None,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        attributeBlackList = [] if attributeBlackList is None else attributeBlackList
        parameters = {
            "INPUT": inputLyr,
            "SELECTED": onlySelected,
            "FLAGS": flagLyr,
            "ATTRIBUTE_BLACK_LIST": attributeBlackList,
            "IGNORE_VIRTUAL_FIELDS": ignoreVirtualFields,
            "IGNORE_PK_FIELDS": excludePrimaryKeys,
            "OUTPUT": outputLyr,
        }
        output = processing.run(
            "dsgtools:removeduplicatedfeatures",
            parameters,
            context=context,
            feedback=feedback,
        )
        return output["OUTPUT"]

    def runApplStylesFromDatabaseToLayers(
        self, inputList, context, styleName, feedback=None, outputLyr=None
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {
            "INPUT_LAYERS": inputList,
            "STYLE_NAME": styleName,
            "OUTPUT": outputLyr,
        }
        output = processing.run(
            "dsgtools:applystylesfromdatabasetolayersalgorithm",
            parameters,
            context=context,
            feedback=feedback,
        )
        return output["OUTPUT"]

    def runMatchAndApplyQmlStylesToLayer(
        self, inputList, context, qmlFolder, feedback=None, outputLyr=None
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {
            "INPUT_LAYERS": inputList,
            "QML_FOLDER": qmlFolder,
            "OUTPUT": outputLyr,
        }
        output = processing.run(
            "dsgtools:matchandapplyqmlstylestolayersalgorithm",
            parameters,
            context=context,
            feedback=feedback,
        )
        return output["OUTPUT"]

    def runAddAutoIncrementalField(
        self,
        inputLyr,
        context,
        feedback=None,
        outputLyr=None,
        fieldName=None,
        start=1,
        sortAscending=True,
        sortNullsFirst=False,
        is_child_algorithm=False,
    ):
        fieldName = "featid" if fieldName is None else fieldName
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {
            "INPUT": inputLyr,
            "FIELD_NAME": fieldName,
            "START": start,
            "GROUP_FIELDS": [],
            "SORT_EXPRESSION": "",
            "SORT_ASCENDING": sortAscending,
            "SORT_NULLS_FIRST": sortNullsFirst,
            "OUTPUT": outputLyr,
        }
        output = processing.run(
            "native:addautoincrementalfield",
            parameters,
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runPolygonsToLines(
        self, inputLyr, context, feedback=None, outputLyr=None, is_child_algorithm=False
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"INPUT": inputLyr, "OUTPUT": outputLyr}
        output = processing.run(
            "native:polygonstolines"
            if Qgis.QGIS_VERSION_INT >= 30600
            else "qgis:polygonstolines",
            parameters,
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runExtractVertices(self, inputLyr, context, feedback=None, outputLyr=None):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"INPUT": inputLyr, "OUTPUT": outputLyr}
        output = processing.run(
            "native:extractvertices", parameters, context=context, feedback=feedback
        )
        return output["OUTPUT"]

    def runExplodeLines(
        self, inputLyr, context, feedback=None, outputLyr=None, is_child_algorithm=False
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"INPUT": inputLyr, "OUTPUT": outputLyr}
        output = processing.run(
            "native:explodelines",
            parameters,
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runMergeVectorLayers(
        self, inputList, context, feedback=None, outputLyr=None, crs=None
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"LAYERS": inputList, "CRS": crs, "OUTPUT": outputLyr}
        output = processing.run(
            "native:mergevectorlayers", parameters, context=context, feedback=feedback
        )
        return output["OUTPUT"]

    def runSaveSelectedFeatures(self, inputLyr, context, feedback=None, outputLyr=None):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"INPUT": inputLyr, "OUTPUT": outputLyr}
        output = processing.run(
            "native:saveselectedfeatures",
            parameters,
            context=context,
            feedback=feedback,
        )
        return output["OUTPUT"]

    def runReprojectLayer(self, layer, targetCrs, output=None, ctx=None, feedback=None):
        """
        Reprojects layer's CRS.
        :param : (QgsVectorLayer) layer to be reprojected.
        :param targetCrs: (QgsCoordinateReferenceSystem) CRS object for the
                          output layer.
        :param output: (QgsVectorLayer) layer accomodate reprojected layer.
        :param ctx: (QgsProcessingContext) processing context in which algorithm
                    should be executed.
        :param feedback: (QgsFeedback) QGIS progress tracking component.
        :return: (QgsVectorLayer) reprojected layer.
        """
        return processing.run(
            "native:reprojectlayer",
            {"INPUT": layer, "OUTPUT": output or "memory:", "TARGET_CRS": targetCrs},
            context=ctx,
            feedback=feedback,
        )["OUTPUT"]

    def runPointOnSurface(
        self,
        inputLyr,
        context,
        allParts=True,
        feedback=None,
        outputLyr=None,
        onlySelected=False,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"INPUT": inputLyr, "ALL_PARTS": allParts, "OUTPUT": outputLyr}
        output = processing.run(
            "native:pointonsurface", parameters, context=context, feedback=feedback
        )
        return output["OUTPUT"]

    def runRemoveDuplicatedGeometries(
        self, inputLyr, context, feedback=None, outputLyr=None, onlySelected=False
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {
            "INPUT": inputLyr,
            "SELECTED": onlySelected,
            "FLAGS": "memory:",
            "OUTPUT": outputLyr,
        }
        output = processing.run(
            "dsgtools:removeduplicatedgeometries",
            parameters,
            context=context,
            feedback=feedback,
        )
        return output["OUTPUT"]

    def runPolygonize(
        self,
        inputLyr,
        context,
        keepFields=False,
        feedback=None,
        outputLyr=None,
        onlySelected=False,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"INPUT": inputLyr, "KEEP_FIELDS": keepFields, "OUTPUT": outputLyr}
        output = processing.run(
            "qgis:polygonize", parameters, context=context, feedback=feedback
        )
        return output["OUTPUT"]

    def runJoinAttributesByLocation(
        self,
        inputLyr,
        joinLyr,
        context,
        predicateList=None,
        joinFields=None,
        method=None,
        discardNonMatching=True,
        feedback=None,
        outputLyr=None,
        unjoinnedLyr=None,
    ):
        predicateList = [0] if predicateList is None else predicateList
        joinFields = [] if joinFields is None else joinFields
        method = 0 if method is None else method
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {
            "INPUT": inputLyr,
            "JOIN": joinLyr,
            "PREDICATE": predicateList,
            "JOIN_FIELDS": joinFields,
            "METHOD": method,
            "DISCARD_NONMATCHING": discardNonMatching,
            "PREFIX": "",
            "OUTPUT": outputLyr,
        }
        output = processing.run(
            "qgis:joinattributesbylocation",
            parameters,
            context=context,
            feedback=feedback,
        )
        return output["OUTPUT"]

    def runLineIntersections(
        self, inputLyr, intersectLyr, context, feedback=None, outputLyr=None
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {
            "INPUT": inputLyr,
            "INTERSECT": intersectLyr,
            "INPUT_FIELDS": [],
            "INTERSECT_FIELDS": [],
            "OUTPUT": outputLyr,
        }
        output = processing.run(
            "native:lineintersections", parameters, context=context, feedback=feedback
        )
        return output["OUTPUT"]

    def runSplitLinesWithLines(
        self,
        inputLyr,
        linesLyr,
        context,
        feedback=None,
        onlySelected=False,
        outputLyr=None,
    ):
        usedInput = (
            inputLyr
            if not onlySelected
            else QgsProcessingFeatureSourceDefinition(inputLyr.id(), True)
        )
        usedLines = (
            linesLyr
            if not onlySelected
            else QgsProcessingFeatureSourceDefinition(linesLyr.id(), True)
        )
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {"INPUT": usedInput, "LINES": usedLines, "OUTPUT": outputLyr}
        output = processing.run(
            "native:splitwithlines", parameters, context=context, feedback=feedback
        )
        return output["OUTPUT"]

    def runAggregate(
        self,
        inputLyr,
        context,
        groupBy=None,
        aggregates=None,
        feedback=None,
        outputLyr=None,
        onlySelected=False,
    ):
        groupBy = "NULL" if groupBy is None else groupBy
        aggregates = [] if aggregates is None else aggregates
        outputLyr = "memory:" if outputLyr is None else outputLyr
        parameters = {
            "INPUT": inputLyr,
            "GROUP_BY": groupBy,
            "AGGREGATES": aggregates,
            "OUTPUT": outputLyr,
        }
        output = processing.run(
            "qgis:aggregate", parameters, context=context, feedback=feedback
        )
        return output["OUTPUT"]

    def runDeaggregate(self, inputLyr, context, feedback=None, onlySelected=False):
        parameters = {"INPUT": inputLyr, "SELECTED": onlySelected}
        output = processing.run(
            "dsgtools:deaggregategeometries",
            parameters,
            context=context,
            feedback=feedback,
        )
        return output

    def runCreateSpatialIndex(
        self, inputLyr, context, feedback=None, is_child_algorithm=False
    ):
        processing.run(
            "native:createspatialindex",
            {"INPUT": inputLyr},
            feedback=feedback,
            context=context,
            is_child_algorithm=is_child_algorithm,
        )
        return None

    def runExtractByLocation(
        self,
        inputLyr,
        intersectLyr,
        context,
        predicate=None,
        feedback=None,
        outputLyr=None,
        is_child_algorithm=False,
    ):
        predicate = [0] if predicate is None else predicate
        outputLyr = "memory:" if outputLyr is None else outputLyr
        output = processing.run(
            "native:extractbylocation",
            {
                "INPUT": inputLyr,
                "INTERSECT": intersectLyr,
                "PREDICATE": predicate,
                "OUTPUT": outputLyr,
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runCreateFieldWithExpression(
        self,
        inputLyr,
        expression,
        fieldName,
        context,
        fieldType=0,
        fieldLength=1000,
        fieldPrecision=0,
        feedback=None,
        outputLyr=None,
        is_child_algorithm=False,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        output = processing.run(
            "native:fieldcalculator",
            {
                "INPUT": inputLyr,
                "FIELD_NAME": fieldName,
                "FIELD_TYPE": fieldType,
                "FIELD_LENGTH": fieldLength,
                "FORMULA": expression,
                "OUTPUT": outputLyr,
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runStringCsvToLayerList(self, stringCSV, context, feedback=None):
        output = processing.run(
            "dsgtools:stringcsvtolayerlistalgorithm",
            {"INPUTLAYERS": stringCSV, "OUTPUT": "memory:"},
            context=context,
            feedback=feedback,
        )
        return output["OUTPUT"]

    def runClipRasterLayer(
        self, inputRaster, mask, context, feedback=None, outputRaster=None, noData=None
    ):
        outputRaster = "TEMPORARY_OUTPUT" if outputRaster is None else outputRaster
        output = processing.run(
            "gdal:cliprasterbymasklayer",
            {
                "INPUT": inputRaster,
                "MASK": mask,
                "SOURCE_CRS": None,
                "TARGET_CRS": None,
                "TARGET_EXTENT": None,
                "NODATA": noData,
                "ALPHA_BAND": False,
                "CROP_TO_CUTLINE": True,
                "KEEP_RESOLUTION": False,
                "SET_RESOLUTION": False,
                "X_RESOLUTION": None,
                "Y_RESOLUTION": None,
                "MULTITHREADING": False,
                "OPTIONS": "",
                "DATA_TYPE": 0,
                "EXTRA": "",
                "OUTPUT": outputRaster,
            },
            # context=context,
            feedback=feedback,
        )
        return output["OUTPUT"]

    def runGrassMapCalcSimple(
        self,
        inputA,
        expression,
        context,
        feedback=None,
        inputB=None,
        inputC=None,
        inputD=None,
        inputE=None,
        inputF=None,
        outputRaster=None,
    ):
        outputRaster = "TEMPORARY_OUTPUT" if outputRaster is None else outputRaster
        output = processing.run(
            "grass7:r.mapcalc.simple",
            {
                "a": inputA,
                "b": inputB,
                "c": inputC,
                "d": inputD,
                "e": inputE,
                "f": inputF,
                "expression": expression,
                "output": outputRaster,
                "GRASS_REGION_PARAMETER": None,
                "GRASS_REGION_CELLSIZE_PARAMETER": 0,
                "GRASS_RASTER_FORMAT_OPT": "",
                "GRASS_RASTER_FORMAT_META": "",
            },
            context=context,
            feedback=feedback,
        )
        return output["output"]

    def runGrassReclass(
        self, inputRaster, expression, context, feedback=None, outputRaster=None
    ):
        outputRaster = "TEMPORARY_OUTPUT" if outputRaster is None else outputRaster
        output = processing.run(
            "grass7:r.reclass",
            {
                "input": inputRaster,
                "rules": "",
                "txtrules": expression,
                "output": outputRaster,
                "GRASS_REGION_PARAMETER": None,
                "GRASS_REGION_CELLSIZE_PARAMETER": 0,
                "GRASS_RASTER_FORMAT_OPT": "",
                "GRASS_RASTER_FORMAT_META": "",
            },
            context=context,
            feedback=feedback,
        )
        return output["output"]

    def runSieve(
        self,
        inputRaster,
        threshold,
        context,
        eightConectedness=False,
        feedback=None,
        outputRaster=None,
    ):
        outputRaster = "TEMPORARY_OUTPUT" if outputRaster is None else outputRaster
        output = processing.run(
            "gdal:sieve",
            {
                "INPUT": inputRaster,
                "THRESHOLD": threshold,
                "EIGHT_CONNECTEDNESS": eightConectedness,
                "NO_MASK": False,
                "MASK_LAYER": None,
                "EXTRA": "",
                "OUTPUT": outputRaster,
            },
            context=context,
            feedback=feedback,
        )
        return output["OUTPUT"]

    def runChaikenSmoothing(
        self,
        inputLyr,
        threshold,
        context,
        feedback=None,
        snap=None,
        minArea=None,
        iterations=None,
        type=None,
        returnError=False,
        flags=None,
        is_child_algorithm=False,
    ):
        """
        Runs simplify GRASS algorithm
        :param inputLyr: (QgsVectorLayer) layer, or layers, to be dissolved.
        :param method: (QgsProcessingParameterEnum) which algorithm would be
            used to simplify lines, in this case, Douglas-Peucker Algorithm.
        :param threshold: (QgsProcessingParameterNumber) give in map units.
            For latitude-longitude locations give in decimal degree.
        :param context: (QgsProcessingContext) processing context.
        :param feedback: (QgsProcessingFeedback) QGIS object to keep track of
            progress/cancelling option.
        :param onlySelected: (QgsProcessingParameterBoolean) process only
            selected features.
        :param outputLyr: (str) URI to output layer.
        :return: (QgsVectorLayer) simplified output layer or layers.
        """
        snap = -1 if snap is None else snap
        minArea = 0.0001 if minArea is None else minArea
        iterations = 1 if iterations is None else iterations
        flags = "memory:" if flags is None else flags
        algType = [0, 1, 2] if type is None else type
        output, error = self.generateGrassOutputAndError()
        parameters = {
            "input": inputLyr,
            "type": algType,
            "cats": "",
            "where": "",
            "method": 8,
            "threshold": threshold,
            "look_ahead": 7,
            "reduction": 50,
            "slide": 0.5,
            "angle_thresh": 3,
            "degree_thresh": 0,
            "closeness_thresh": 0,
            "betweeness_thresh": 0,
            "alpha": 1,
            "beta": 1,
            "iterations": iterations,
            "-t": False,
            "-l": True,
            "output": output,
            "error": error,
            "GRASS_REGION_PARAMETER": None,
            "GRASS_SNAP_TOLERANCE_PARAMETER": snap,
            "GRASS_MIN_AREA_PARAMETER": minArea,
            "GRASS_OUTPUT_TYPE_PARAMETER": 0,
            "GRASS_VECTOR_DSCO": "",
            "GRASS_VECTOR_LCO": "",
        }
        outputDict = processing.run(
            "grass7:v.generalize",
            parameters,
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return self.getGrassReturn(outputDict, context, returnError=returnError)

    def runGdalPolygonize(
        self,
        inputRaster,
        context,
        band=1,
        field=None,
        eightConectedness=False,
        feedback=None,
        outputLyr=None,
        is_child_algorithm=False,
    ):
        outputLyr = "TEMPORARY_OUTPUT" if outputLyr is None else outputLyr
        field = "DN" if field is None else field
        output = processing.run(
            "gdal:polygonize",
            {
                "INPUT": inputRaster,
                "BAND": band,
                "FIELD": field,
                "EIGHT_CONNECTEDNESS": eightConectedness,
                "EXTRA": "",
                "OUTPUT": outputLyr,
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runExtractSpecificVertices(
        self, inputLyr, vertices, context, feedback=None, outputLyr=None
    ):
        outputLyr = "TEMPORARY_OUTPUT" if outputLyr is None else outputLyr
        output = processing.run(
            "native:extractspecificvertices",
            {
                "INPUT": inputLyr,
                "VERTICES": vertices,
                "OUTPUT": outputLyr,
            },
            context=context,
            feedback=feedback,
        )
        return output["OUTPUT"]

    def runCreateGrid(
        self,
        extent,
        crs,
        hSpacing,
        vSpacing,
        context,
        type=2,
        feedback=None,
        outputLyr=None,
        hOverlay=0,
        vOverlay=0,
        is_child_algorithm=False,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        output = processing.run(
            "native:creategrid",
            {
                "TYPE": type,
                "EXTENT": extent,
                "HSPACING": hSpacing,
                "VSPACING": vSpacing,
                "HOVERLAY": hOverlay,
                "VOVERLAY": vOverlay,
                "CRS": crs,
                "OUTPUT": outputLyr,
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runExtendLines(
        self,
        inputLyr,
        startDistance,
        endDistance,
        context,
        feedback=None,
        outputLyr=None,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        output = processing.run(
            "native:extendlines",
            {
                "INPUT": inputLyr,
                "START_DISTANCE": startDistance,
                "END_DISTANCE": endDistance,
                "OUTPUT": outputLyr,
            },
            context=context,
            feedback=feedback,
        )
        return output["OUTPUT"]

    def runIdentifyUnsharedVertexOnIntersectionsAlgorithm(
        self,
        pointLayerList,
        lineLayerList,
        polygonLayerList,
        context,
        onlySelected=False,
        feedback=None,
        outputLyr=None,
        is_child_algorithm=False,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        output = processing.run(
            "dsgtools:identifyunsharedvertexonintersectionsalgorithm",
            {
                "INPUT_POINTS": pointLayerList,
                "INPUT_LINES": lineLayerList,
                "INPUT_POLYGONS": polygonLayerList,
                "SELECTED": onlySelected,
                "FLAGS": outputLyr,
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["FLAGS"]

    def runIdentifyUnsharedVertexOnSharedEdgesAlgorithm(
        self,
        lineLayerList,
        polygonLayerList,
        searchRadius,
        context,
        onlySelected=False,
        feedback=None,
        outputLyr=None,
        is_child_algorithm=False,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        output = processing.run(
            "dsgtools:identifyunsharedvertexonsharededgesalgorithm",
            {
                "INPUT_LINES": lineLayerList,
                "INPUT_POLYGONS": polygonLayerList,
                "SELECTED": onlySelected,
                "SEARCH_RADIUS": searchRadius,
                "FLAGS": outputLyr,
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["FLAGS"]

    def runShortestLine(
        self,
        sourceLayer,
        destinationLayer,
        context,
        method=0,
        neighbors=1,
        maxDistance=None,
        feedback=None,
        outputLyr=None,
        is_child_algorithm=False,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        output = processing.run(
            "native:shortestline",
            {
                "SOURCE": sourceLayer,
                "DESTINATION": destinationLayer,
                "METHOD": method,
                "NEIGHBORS": neighbors,
                "DISTANCE": maxDistance,
                "OUTPUT": outputLyr,
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runRetainFields(
        self,
        inputLayer,
        fields,
        context,
        feedback=None,
        outputLyr=None,
        is_child_algorithm=False,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        output = processing.run(
            "native:retainfields",
            {"INPUT": inputLayer, "FIELDS": fields, "OUTPUT": "TEMPORARY_OUTPUT"},
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runExtractByExtent(
        self,
        inputLayer,
        extent,
        context,
        clip=True,
        feedback=None,
        outputLyr=None,
        is_child_algorithm=False,
    ):
        outputLyr = "memory:" if outputLyr is None else outputLyr
        output = processing.run(
            "native:extractbyextent",
            {
                "INPUT": inputLayer,
                "EXTENT": extent,
                "CLIP": clip,
                "OUTPUT": outputLyr,
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        return output["OUTPUT"]

    def runSelectByLocation(
        self,
        inputLyr,
        intersectLyr,
        context,
        predicate=None,
        method=None,
        feedback=None,
        is_child_algorithm=False,
    ):
        predicate = [0] if predicate is None else predicate
        method = [0] if method is None else method
        processing.run(
            "native:selectbylocation",
            {
                "INPUT": inputLyr,
                "INTERSECT": intersectLyr,
                "PREDICATE": predicate,
                "METHOD": method,
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
