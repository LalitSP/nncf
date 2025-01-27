# Copyright (c) 2024 Intel Corporation
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Union

from torch import Tensor

from nncf.common.graph.graph import NNCFNode
from nncf.common.graph.transformations.commands import TargetType
from nncf.common.graph.transformations.commands import TransformationPriority
from nncf.common.quantization.structs import NonWeightQuantizerId
from nncf.torch.graph.transformations.commands import ExtraCompressionModuleType
from nncf.torch.graph.transformations.commands import PTBiasCorrectionCommand
from nncf.torch.graph.transformations.commands import PTInsertionCommand
from nncf.torch.graph.transformations.commands import PTSharedFnInsertionCommand
from nncf.torch.graph.transformations.commands import PTTargetPoint
from nncf.torch.graph.transformations.commands import PTWeightUpdateCommand
from nncf.torch.quantization.layers import BaseQuantizer


def create_bias_correction_command(node: NNCFNode, bias_value: Tensor) -> PTBiasCorrectionCommand:
    """
     Creates bias correction command.

    :param node: The node in the NNCF graph that corresponds to operation with bias.
    :param bias_value: The new bias value that will be set.
    :return: The `PTBiasCorrectionCommand` command to update bias.
    """
    target_point = PTTargetPoint(TargetType.LAYER, node.node_name)
    return PTBiasCorrectionCommand(target_point, bias_value)


def create_command_to_update_weight(node: NNCFNode, weight_value: Tensor) -> PTWeightUpdateCommand:
    """
     Creates weight update command.

    :param node: The node in the NNCF graph that corresponds to operation with weight.
    :param weight_value: The new weight value that will be set.
    :return: The `PTWeightUpdateCommand` command to update weight.
    """
    target_point = PTTargetPoint(TargetType.LAYER, node.node_name)
    return PTWeightUpdateCommand(target_point, weight_value)


def create_quantizer_insertion_command(
    target_point: PTTargetPoint, quantizer: BaseQuantizer
) -> Union[PTInsertionCommand, PTSharedFnInsertionCommand]:
    if target_point.type is TargetType.OPERATION_WITH_WEIGHTS:
        return PTInsertionCommand(target_point, quantizer, TransformationPriority.QUANTIZATION_PRIORITY)

    quantizer_id = NonWeightQuantizerId(target_point.target_node_name, target_point.input_port_id)
    storage_key = str(quantizer_id)
    return PTSharedFnInsertionCommand(
        target_points=[target_point],
        fn=quantizer,
        op_unique_name=storage_key,
        compression_module_type=ExtraCompressionModuleType.EXTERNAL_QUANTIZER,
        priority=TransformationPriority.QUANTIZATION_PRIORITY,
    )
