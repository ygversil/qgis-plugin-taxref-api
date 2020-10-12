# -*- coding: utf-8 -*-

"""
/***************************************************************************
 TaxrefApi
                                 A QGIS plugin
 This plugin install a processing algorithm to download and join data from
 French TAXREF API, provided by the French National Museum of Natural History
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-10-09
        copyright            : (C) 2020 by Yann Voté
        email                : ygversil@lilo.org
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

__author__ = 'Yann Voté'
__date__ = '2020-10-09'
__copyright__ = '(C) 2020 by Yann Voté'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


from pathlib import Path
from urllib.parse import urljoin
import json
import yaml

from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
from qgis.PyQt.QtCore import QUrl, QVariant
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import (
    QgsBlockingNetworkRequest,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsProcessing,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterField,
)


_BARCELONA_CONVENTION_STATUS_TYPE_URI = 'https://taxref.mnhn.fr/api/status/types/BARC'
_BARCELONA_CONVENTION_STATUS_CODE_FIELD_NAME = 'convention_barcelone_code'
_BARCELONA_CONVENTION_STATUS_TITLE_FIELD_NAME = 'convention_barcelone_libelle'
_BERN_CONVENTION_STATUS_TYPE_URI = 'https://taxref.mnhn.fr/api/status/types/BERN'
_BERN_CONVENTION_STATUS_CODE_FIELD_NAME = 'convention_bern_code'
_BERN_CONVENTION_STATUS_TITLE_FIELD_NAME = 'convention_bern_libelle'
_BIRDS_DIRECTIVE_STATUS_TYPE_URI = 'https://taxref.mnhn.fr/api/status/types/DO'
_BIRDS_DIRECTIVE_STATUS_CODE_FIELD_NAME = 'directive_oiseaux_code'
_BIRDS_DIRECTIVE_STATUS_TITLE_FIELD_NAME = 'directive_oiseaux_libelle'
_BONN_CONVENTION_STATUS_TYPE_URI = 'https://taxref.mnhn.fr/api/status/types/BONN'
_BONN_CONVENTION_STATUS_CODE_FIELD_NAME = 'convention_bonn_code'
_BONN_CONVENTION_STATUS_TITLE_FIELD_NAME = 'convention_bonn_libelle'
_DEPARTMENT_ID_MNHN_PREFIX = 'INSEEND'
_EUROPEAN_RED_LIST_STATUS_TYPE_URI = 'https://taxref.mnhn.fr/api/status/types/LRE'
_EUROPEAN_RED_LIST_STATUS_CODE_FIELD_NAME = 'liste_rouge_europeenne_code'
_EUROPEAN_RED_LIST_STATUS_TITLE_FIELD_NAME = 'liste_rouge_europeenne_libelle'
_HABITATS_DIRECTIVE_STATUS_TYPE_URI = 'https://taxref.mnhn.fr/api/status/types/DH'
_HABITATS_DIRECTIVE_STATUS_CODE_FIELD_NAME = 'directive_habitats_code'
_HABITATS_DIRECTIVE_STATUS_TITLE_FIELD_NAME = 'directive_habitats_libelle'
_LOCAL_RED_LIST_STATUS_TYPE_URI = 'https://taxref.mnhn.fr/api/status/types/LRR'
_LOCAL_RED_LIST_STATUS_CODE_FIELD_NAME = 'liste_rouge_regionale_{reg_code}_code'
_LOCAL_RED_LIST_STATUS_LOCATION_FIELD_NAME = 'liste_rouge_regionale_{reg_code}_region'
_LOCAL_RED_LIST_STATUS_TITLE_FIELD_NAME = 'liste_rouge_regionale_{reg_code}_libelle'
_NATIONAL_RED_LIST_STATUS_TYPE_URI = 'https://taxref.mnhn.fr/api/status/types/LRN'
_NATIONAL_RED_LIST_STATUS_CODE_FIELD_NAME = 'liste_rouge_nationale_code'
_NATIONAL_RED_LIST_STATUS_TITLE_FIELD_NAME = 'liste_rouge_nationale_libelle'
_OLD_REGION_ID_MNHN_PREFIX = 'INSEER'
_OSPAR_CONVENTION_STATUS_TYPE_URI = 'https://taxref.mnhn.fr/api/status/types/OSPAR'
_OSPAR_CONVENTION_STATUS_CODE_FIELD_NAME = 'convention_ospar_code'
_OSPAR_CONVENTION_STATUS_TITLE_FIELD_NAME = 'convention_ospar_libelle'
_REGION_ID_MNHN_PREFIX = 'INSEENR'
_STATUS_PATH = 'taxa/{cd_ref}/status/lines'
_TAXREF_API_BASE_URL = 'https://taxref.mnhn.fr/api/'
_WORLD_RED_LIST_STATUS_TYPE_URI = 'https://taxref.mnhn.fr/api/status/types/LRM'
_WORLD_RED_LIST_STATUS_CODE_FIELD_NAME = 'liste_rouge_mondiale_code'
_WORLD_RED_LIST_STATUS_TITLE_FIELD_NAME = 'liste_rouge_mondiale_libelle'
_REGIONAL_ZNIEFF_CRITICAL_STATUS_TYPE_URI = 'https://taxref.mnhn.fr/api/status/types/ZDET'
_REGIONAL_ZNIEFF_CRITICAL_STATUS_CODE_FIELD_NAME = 'det_znieff_regionale_{reg_code}_code'
_REGIONAL_ZNIEFF_CRITICAL_STATUS_LOCATION_FIELD_NAME = 'det_znieff_regionale_{reg_code}_region'
_REGIONAL_ZNIEFF_CRITICAL_STATUS_TITLE_FIELD_NAME = 'det_znieff_regionale_{reg_code}_libelle'


def _added_attributes(cd_ref, region_list, old_region_list, feedback):
    attributes = dict()
    if not cd_ref:
        return attributes
    feedback.pushDebugInfo('Fetching status data for CD_REF {}...'.format(cd_ref))
    res = _get_json_results(_STATUS_PATH.format(cd_ref=cd_ref), feedback)
    if not res:
        feedback.reportError('Failed to fetch data for CD_REF {}. Ignoring...'.format(cd_ref))
        return attributes
    status_list = res['status']
    _add_supra_national_status(attributes, status_list, _BARCELONA_CONVENTION_STATUS_TYPE_URI,
                               _BARCELONA_CONVENTION_STATUS_CODE_FIELD_NAME,
                               _BARCELONA_CONVENTION_STATUS_TITLE_FIELD_NAME)
    _add_supra_national_status(attributes, status_list, _BERN_CONVENTION_STATUS_TYPE_URI,
                               _BERN_CONVENTION_STATUS_CODE_FIELD_NAME,
                               _BERN_CONVENTION_STATUS_TITLE_FIELD_NAME)
    _add_supra_national_status(attributes, status_list, _BONN_CONVENTION_STATUS_TYPE_URI,
                               _BONN_CONVENTION_STATUS_CODE_FIELD_NAME,
                               _BONN_CONVENTION_STATUS_TITLE_FIELD_NAME)
    _add_supra_national_status(attributes, status_list, _OSPAR_CONVENTION_STATUS_TYPE_URI,
                               _OSPAR_CONVENTION_STATUS_CODE_FIELD_NAME,
                               _OSPAR_CONVENTION_STATUS_TITLE_FIELD_NAME)
    _add_supra_national_status(attributes, status_list, _HABITATS_DIRECTIVE_STATUS_TYPE_URI,
                               _HABITATS_DIRECTIVE_STATUS_CODE_FIELD_NAME,
                               _HABITATS_DIRECTIVE_STATUS_TITLE_FIELD_NAME)
    _add_supra_national_status(attributes, status_list, _BIRDS_DIRECTIVE_STATUS_TYPE_URI,
                               _BIRDS_DIRECTIVE_STATUS_CODE_FIELD_NAME,
                               _BIRDS_DIRECTIVE_STATUS_TITLE_FIELD_NAME)
    _add_supra_national_status(attributes, status_list, _WORLD_RED_LIST_STATUS_TYPE_URI,
                               _WORLD_RED_LIST_STATUS_CODE_FIELD_NAME,
                               _WORLD_RED_LIST_STATUS_TITLE_FIELD_NAME)
    _add_supra_national_status(attributes, status_list, _EUROPEAN_RED_LIST_STATUS_TYPE_URI,
                               _EUROPEAN_RED_LIST_STATUS_CODE_FIELD_NAME,
                               _EUROPEAN_RED_LIST_STATUS_TITLE_FIELD_NAME)
    _add_supra_national_status(attributes, status_list, _NATIONAL_RED_LIST_STATUS_TYPE_URI,
                               _NATIONAL_RED_LIST_STATUS_CODE_FIELD_NAME,
                               _NATIONAL_RED_LIST_STATUS_TITLE_FIELD_NAME)
    for region_dict in region_list:
        reg_code = region_dict['insee_code']
        region_mnhn_id = _location_id(region_dict, 'region')
        attributes[_LOCAL_RED_LIST_STATUS_LOCATION_FIELD_NAME.format(reg_code=reg_code)] = \
            region_dict['name']
        _add_local_status(
            attributes, status_list, _LOCAL_RED_LIST_STATUS_TYPE_URI, region_mnhn_id,
            _LOCAL_RED_LIST_STATUS_CODE_FIELD_NAME.format(reg_code=reg_code),
            _LOCAL_RED_LIST_STATUS_TITLE_FIELD_NAME.format(reg_code=reg_code),
        )
        attributes[_REGIONAL_ZNIEFF_CRITICAL_STATUS_LOCATION_FIELD_NAME.format(reg_code=reg_code)] \
            = region_dict['name']
        _add_local_status(
            attributes, status_list, _REGIONAL_ZNIEFF_CRITICAL_STATUS_TYPE_URI, region_mnhn_id,
            _REGIONAL_ZNIEFF_CRITICAL_STATUS_CODE_FIELD_NAME.format(reg_code=reg_code),
            _REGIONAL_ZNIEFF_CRITICAL_STATUS_TITLE_FIELD_NAME.format(reg_code=reg_code),
        )
    for old_region_dict in old_region_list:
        reg_code = old_region_dict['insee_code']
        region_mnhn_id = _location_id(old_region_dict, 'old_region')
        attributes[_LOCAL_RED_LIST_STATUS_LOCATION_FIELD_NAME.format(reg_code=reg_code)] = \
            old_region_dict['name']
        _add_local_status(
            attributes, status_list, _LOCAL_RED_LIST_STATUS_TYPE_URI, region_mnhn_id,
            _LOCAL_RED_LIST_STATUS_CODE_FIELD_NAME.format(reg_code=reg_code),
            _LOCAL_RED_LIST_STATUS_TITLE_FIELD_NAME.format(reg_code=reg_code),
        )
        attributes[_REGIONAL_ZNIEFF_CRITICAL_STATUS_LOCATION_FIELD_NAME.format(reg_code=reg_code)] \
            = old_region_dict['name']
        _add_local_status(
            attributes, status_list, _REGIONAL_ZNIEFF_CRITICAL_STATUS_TYPE_URI, region_mnhn_id,
            _REGIONAL_ZNIEFF_CRITICAL_STATUS_CODE_FIELD_NAME.format(reg_code=reg_code),
            _REGIONAL_ZNIEFF_CRITICAL_STATUS_TITLE_FIELD_NAME.format(reg_code=reg_code),
        )
    feedback.pushDebugInfo('Added attributes: {}'.format(str(attributes)))
    return attributes


def _add_local_status(attributes, status_list, status_type, location_id, code_field_name,
                      title_field_name):
    code = None
    title = None
    for status_dict in status_list:
        if (status_dict['_links']['statusType']['href'] == status_type
                and status_dict['locationId'] == location_id):
            code = status_dict['statusCode']
            title = status_dict['statusName']
            break
    attributes[code_field_name] = code
    attributes[title_field_name] = title


def _add_supra_national_status(attributes, status_list, status_type, code_field_name,
                               title_field_name):
    code = None
    title = None
    for status_dict in status_list:
        if status_dict['_links']['statusType']['href'] == status_type:
            code = status_dict['statusCode']
            title = status_dict['statusName']
            break
    attributes[code_field_name] = code
    attributes[title_field_name] = title


def _get_json_results(path, feedback):
    req = QgsBlockingNetworkRequest()
    req_status = req.get(QNetworkRequest(QUrl(urljoin(_TAXREF_API_BASE_URL, path))))
    if req_status != QgsBlockingNetworkRequest.NoError:
        for error_name in ('NetworkError', 'TimeoutError', 'ServerExceptionError'):
            if req_status == getattr(QgsBlockingNetworkRequest, error_name):
                feedback.reportError('{}: {}'.format(error_name, req.errorMessage()))
                break
        return None
    return json.loads(bytes(req.reply().content()))['_embedded']


def _location_id(location_dict, location_type):
    template = '{prefix}{code}'
    code = location_dict['insee_code']
    if location_type == 'region':
        return template.format(
            prefix=(_REGION_ID_MNHN_PREFIX if not location_dict['is_same_than_old_region'] else
                    _OLD_REGION_ID_MNHN_PREFIX),
            code=code,
        )
    elif location_type == 'old_region':
        return template.format(prefix=_OLD_REGION_ID_MNHN_PREFIX, code=code)


class JoinTaxrefDataByCdRefAlgorithm(QgisAlgorithm):

    INPUT = 'INPUT'
    CD_REF_FIELD = 'CD_REF_FIELD'
    REGION = 'REGION'
    INCLUDE_OLD_REGIONS = 'INCLUDE_OLD_REGIONS'
    OUTPUT = 'OUTPUT'

    def name(self):
        return 'jointaxrefdatabycdref'

    def displayName(self):
        return self.tr('Join TAXREF data by CD_REF')

    def groupId(self):
        return 'taxref'

    def group(self):
        return self.tr('TAXREF')

    def initAlgorithm(self, config):
        with (Path(__file__).parent / 'yml_data' / 'regions.yml').open(encoding='utf-8') as f:
            region_list = yaml.load(f.read(), Loader=yaml.SafeLoader)
        region_list = [region_dict['name'] for region_dict in region_list]
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.CD_REF_FIELD,
                self.tr('CD_REF field'),
                None,
                self.INPUT,
                QgsProcessingParameterField.Numeric,
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.REGION,
                self.tr('Regions for which to download local status'),
                region_list,
                allowMultiple=True,
                defaultValue=None,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.INCLUDE_OLD_REGIONS,
                self.tr('Include old regions status'),
                region_list,
                False,
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        cd_ref_field = self.parameterAsString(parameters, self.CD_REF_FIELD, context)
        region_indices = self.parameterAsEnums(parameters, self.REGION, context)
        include_old_regions = self.parameterAsBoolean(parameters, self.INCLUDE_OLD_REGIONS, context)
        with (Path(__file__).parent / 'yml_data' / 'regions.yml').open(encoding='utf-8') as f:
            region_list = yaml.load(f.read(), Loader=yaml.SafeLoader)
        region_list = [region_list[i] for i in region_indices]
        fields = source.fields()
        added_fields = []
        for field_name, field_type in (
            (_BARCELONA_CONVENTION_STATUS_CODE_FIELD_NAME, QVariant.String),
            (_BARCELONA_CONVENTION_STATUS_TITLE_FIELD_NAME, QVariant.String),
            (_BERN_CONVENTION_STATUS_CODE_FIELD_NAME, QVariant.String),
            (_BERN_CONVENTION_STATUS_TITLE_FIELD_NAME, QVariant.String),
            (_BONN_CONVENTION_STATUS_CODE_FIELD_NAME, QVariant.String),
            (_BONN_CONVENTION_STATUS_TITLE_FIELD_NAME, QVariant.String),
            (_OSPAR_CONVENTION_STATUS_CODE_FIELD_NAME, QVariant.String),
            (_OSPAR_CONVENTION_STATUS_TITLE_FIELD_NAME, QVariant.String),
            (_HABITATS_DIRECTIVE_STATUS_CODE_FIELD_NAME, QVariant.String),
            (_HABITATS_DIRECTIVE_STATUS_TITLE_FIELD_NAME, QVariant.String),
            (_BIRDS_DIRECTIVE_STATUS_CODE_FIELD_NAME, QVariant.String),
            (_BIRDS_DIRECTIVE_STATUS_TITLE_FIELD_NAME, QVariant.String),
            (_WORLD_RED_LIST_STATUS_CODE_FIELD_NAME, QVariant.String),
            (_WORLD_RED_LIST_STATUS_TITLE_FIELD_NAME, QVariant.String),
            (_EUROPEAN_RED_LIST_STATUS_CODE_FIELD_NAME, QVariant.String),
            (_EUROPEAN_RED_LIST_STATUS_TITLE_FIELD_NAME, QVariant.String),
            (_NATIONAL_RED_LIST_STATUS_CODE_FIELD_NAME, QVariant.String),
            (_NATIONAL_RED_LIST_STATUS_TITLE_FIELD_NAME, QVariant.String),
        ):
            fields.append(QgsField(field_name, field_type))
            added_fields.append(field_name)
        for region_dict in region_list:
            reg_code = region_dict['insee_code']
            for field_name, field_type in (
                (_LOCAL_RED_LIST_STATUS_LOCATION_FIELD_NAME.format(reg_code=reg_code),
                 QVariant.String),
                (_LOCAL_RED_LIST_STATUS_CODE_FIELD_NAME.format(reg_code=reg_code),
                 QVariant.String),
                (_LOCAL_RED_LIST_STATUS_TITLE_FIELD_NAME.format(reg_code=reg_code),
                 QVariant.String),
                (_REGIONAL_ZNIEFF_CRITICAL_STATUS_LOCATION_FIELD_NAME.format(reg_code=reg_code),
                 QVariant.String),
                (_REGIONAL_ZNIEFF_CRITICAL_STATUS_CODE_FIELD_NAME.format(reg_code=reg_code),
                 QVariant.Bool),
                (_REGIONAL_ZNIEFF_CRITICAL_STATUS_TITLE_FIELD_NAME.format(reg_code=reg_code),
                 QVariant.String),
            ):
                fields.append(QgsField(field_name, field_type))
                added_fields.append(field_name)
        if not include_old_regions:
            old_region_list = []
        else:
            with (Path(__file__).parent / 'yml_data'
                  / 'old_regions.yml').open(encoding='utf-8') as f:
                old_region_list = yaml.load(f.read(), Loader=yaml.SafeLoader)
        parent_codes = set(region_dict['insee_code'] for region_dict in region_list)
        old_region_list = list(
            filter(lambda old_region_dict: old_region_dict['parent_code'] in parent_codes,
                   old_region_list)
        )
        for old_region_dict in old_region_list:
            reg_code = old_region_dict['insee_code']
            for field_name, field_type in (
                (_LOCAL_RED_LIST_STATUS_LOCATION_FIELD_NAME.format(reg_code=reg_code),
                 QVariant.String),
                (_LOCAL_RED_LIST_STATUS_CODE_FIELD_NAME.format(reg_code=reg_code),
                 QVariant.String),
                (_LOCAL_RED_LIST_STATUS_TITLE_FIELD_NAME.format(reg_code=reg_code),
                 QVariant.String),
                (_REGIONAL_ZNIEFF_CRITICAL_STATUS_LOCATION_FIELD_NAME.format(reg_code=reg_code),
                 QVariant.String),
                (_REGIONAL_ZNIEFF_CRITICAL_STATUS_CODE_FIELD_NAME.format(reg_code=reg_code),
                 QVariant.Bool),
                (_REGIONAL_ZNIEFF_CRITICAL_STATUS_TITLE_FIELD_NAME.format(reg_code=reg_code),
                 QVariant.String),
            ):
                fields.append(QgsField(field_name, field_type))
                added_fields.append(field_name)
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                                               context, fields, source.wkbType(),
                                               source.sourceCrs())
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        for i, in_feature in enumerate(features):
            if feedback.isCanceled():
                break
            cd_ref = in_feature.attribute(cd_ref_field)
            added_attributes_dict = _added_attributes(cd_ref, region_list, old_region_list,
                                                      feedback)
            out_feature = QgsFeature()
            out_feature.setGeometry(in_feature.geometry())
            out_attributes = in_feature.attributes()
            for field_name in added_fields:
                out_attributes.append(added_attributes_dict.get(field_name))
            out_feature.setAttributes(out_attributes)
            sink.addFeature(out_feature, QgsFeatureSink.FastInsert)
            feedback.setProgress(int(i * total))
        return {self.OUTPUT: dest_id}
