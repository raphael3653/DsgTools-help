# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DsgTools
                                 A QGIS plugin
 Brazilian Army Cartographic Production Tools
                              -------------------
        begin                : 2019-09-17
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Philipe Borba - Cartographic Engineer @ Brazilian Army
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
from PyQt5.QtCore import QCoreApplication

from DsgTools.core.dsgEnums import DsgEnums
from DsgTools.core.Factories.DbFactory.dbFactory import DbFactory
from DsgTools.core.Factories.LayerLoaderFactory.layerLoaderFactory import (
    LayerLoaderFactory,
)
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsDataSourceUri,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingMultiStepFeedback,
    QgsProcessingOutputMultipleLayers,
    QgsProcessingOutputVectorLayer,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterCrs,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterExpression,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterFile,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
    QgsProcessingParameterType,
    QgsProcessingParameterVectorLayer,
    QgsProcessingUtils,
    QgsProject,
    QgsSpatialIndex,
    QgsWkbTypes,
    QgsMapLayer,
)
from qgis.utils import iface


class LoadLayersFromPostgisAlgorithm(QgsProcessingAlgorithm):
    HOST = "HOST"
    PORT = "PORT"
    DATABASE = "DATABASE"
    USER = "USER"
    PASSWORD = "PASSWORD"
    LAYER_LIST = "LAYER_LIST"
    LOAD_TO_CANVAS = "LOAD_TO_CANVAS"
    UNIQUE_LOAD = "UNIQUE_LOAD"
    OUTPUT = "OUTPUT"

    def initAlgorithm(self, config):
        """
        Parameter setting.
        """
        self.addParameter(QgsProcessingParameterString(self.HOST, self.tr("Host")))
        self.addParameter(QgsProcessingParameterString(self.PORT, self.tr("Port")))
        self.addParameter(
            QgsProcessingParameterString(self.DATABASE, self.tr("Database"))
        )
        self.addParameter(QgsProcessingParameterString(self.USER, self.tr("User")))
        self.addParameter(
            QgsProcessingParameterString(self.PASSWORD, self.tr("Password"))
        )
        self.addParameter(
            QgsProcessingParameterString(self.LAYER_LIST, self.tr("Layer List"))
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.LOAD_TO_CANVAS, self.tr("Load layers to canvas"), defaultValue=True
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.UNIQUE_LOAD, self.tr("Unique load"), defaultValue=True
            )
        )

        self.addOutput(
            QgsProcessingOutputMultipleLayers(self.OUTPUT, self.tr("Loaded layers"))
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        host = self.parameterAsString(parameters, self.HOST, context)
        port = self.parameterAsString(parameters, self.PORT, context)
        database = self.parameterAsString(parameters, self.DATABASE, context)
        user = self.parameterAsString(parameters, self.USER, context)
        password = self.parameterAsString(parameters, self.PASSWORD, context)
        layerStringList = self.parameterAsString(parameters, self.LAYER_LIST, context)
        loadToCanvas = self.parameterAsBool(parameters, self.LOAD_TO_CANVAS, context)
        uniqueLoad = self.parameterAsBool(parameters, self.UNIQUE_LOAD, context)
        abstractDb = self.getAbstractDb(host, port, database, user, password)
        inputParamList = layerStringList.split(",")
        unloadedLayerNames = self.getUnloadedLayerNames(inputParamList)
        if not unloadedLayerNames:
            return {self.OUTPUT: []}
        layerLoader = LayerLoaderFactory().makeLoader(iface, abstractDb)
        if loadToCanvas:
            iface.mapCanvas().freeze(True)
        outputLayers = layerLoader.loadLayersInsideProcessing(
            unloadedLayerNames,
            uniqueLoad=uniqueLoad,
            addToCanvas=loadToCanvas,
            feedback=feedback,
        )
        if loadToCanvas:
            iface.mapCanvas().freeze(False)
        return {
            self.OUTPUT: self.getLoadedLayerIds(layerNamesFilter=unloadedLayerNames)
        }

    def getLoadedLayerIds(self, layerNamesFilter):
        layerIds = []
        for l in QgsProject.instance().mapLayers().values():
            if not (l.type() == QgsMapLayer.VectorLayer):
                continue
            layerName = None
            if l.providerType() == "postgres":
                layerName = l.dataProvider().uri().table()
            elif l.providerType() == "ogr":
                layerName = (
                    l.dataProvider().uri().uri().split("|")[-1].split("=")[-1][1:-1]
                )
            if not layerName or not (layerName in layerNamesFilter):
                continue
            layerIds.append(l.id())
        return layerIds

    def getUnloadedLayerNames(self, layerNames):
        loadedLayerNames = []
        for l in QgsProject.instance().mapLayers().values():
            if not (l.type() == QgsMapLayer.VectorLayer):
                continue
            layerName = None
            if l.providerType() == "postgres":
                layerName = l.dataProvider().uri().table()
            elif l.providerType() == "ogr":
                layerName = (
                    l.dataProvider().uri().uri().split("|")[-1].split("=")[-1][1:-1]
                )
            if not layerName or not (layerName in layerNames):
                continue
            loadedLayerNames.append(layerName)
        return list(set(layerNames) - set(loadedLayerNames))

    def getAbstractDb(self, host, port, database, user, password):
        abstractDb = DbFactory().createDbFactory(DsgEnums.DriverPostGIS)
        abstractDb.connectDatabaseWithParameters(host, port, database, user, password)
        return abstractDb

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return "loadlayersfrompostgisalgorithm"

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr("Load Layers From Postgis")

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr("Layer Management Algorithms")

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return "DSGTools: Layer Management Algorithms"

    def tr(self, string):
        return QCoreApplication.translate("LoadLayersFromPostgisAlgorithm", string)

    def createInstance(self):
        return LoadLayersFromPostgisAlgorithm()

    def flags(self):
        """
        This process is not thread safe due to the fact that removeChildNode
        method from QgsLayerTreeGroup is not thread safe.
        """
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading
