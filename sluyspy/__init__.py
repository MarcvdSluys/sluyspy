# -*- coding: utf-8 -*-
# SPDX-License-Identifier: EUPL-1.2
#  
#  Copyright (c) 2022-2023  Marc van der Sluys - marc.vandersluys.nl
#   
#  This file is part of the sluyspy Python package:
#  Marc van der Sluys' personal Python modules.
#  See: https://github.com/MarcvdSluys/sluyspy
#   
#  This is free software: you can redistribute it and/or modify it under the terms of the European Union
#  Public Licence 1.2 (EUPL 1.2).  This software is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#  PURPOSE.  See the EU Public Licence for more details.  You should have received a copy of the European
#  Union Public Licence along with this code.  If not, see <https://www.eupl.eu/1.2/en/>.


"""sluyspy package

Marc van der Sluys' personal Python modules.
The code is being developed by `Marc van der Sluys <http://marc.vandersluys.nl>`_ of the department of
Astrophysics at the Radboud University Nijmegen, the Institute of Nuclear and High-Energy Physics (Nikhef),
and the Institute for Gravitational and Subatomic Physics (GRASP) at Utrecht University, all in The Netherlands.
The sluyspy package can be used under the conditions of the EUPL 1.2 licence.  These pages contain the API
documentation.  For more information on the Python package, licence and source code, see the
`sluyspy GitHub page <https://github.com/MarcvdSluys/sluyspy>`_.
"""


name = 'sluyspy'

from . import cli
from . import plot
from . import text
from . import weather


# Avoid F401 "'module' imported but unused" warnings:
if False:
    print(cli, plot, text, weather)
