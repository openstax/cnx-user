#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###


"""
THis exists solely to provide less typing for a "leaf node" 
in a simple realtional schema (1:M and 1:M-N:1) when used with SQLAlchemy

SA does not support class based inheritence in the normal Python way for objects inheriting from Base.  Thus we have those objects perform multiple inheritence...


"""
import json
import sqlalchemy.types
import datetime


class CNXBase():
    def from_dict(self, userprofile_dict):
        """
        SHould test for schema validity etc.

        """
        d = userprofile_dict
        for k in d: 
            setattr(self, k, d[k])

    def to_dict(self):
        """Return self as a dict, suitable for jsonifying """

        d = {}
        for col in self.__table__.columns:
            d[col.name] = self.safe_type_out(col)
        return d

    def jsonify(self):
        """Helper function that returns simple json repr """
        selfd = self.to_dict()
        jsonstr = json.dumps(selfd)  # here use the Json ENcoder???
        return jsonstr

    def safe_type_out(self, col):
        """return the value of a coulmn field safely as something that
           json can use This is essentially a JSONEncoder sublclass
           inside this object.
        """

        if isinstance(type(col.type), sqlalchemy.types.DateTime):
            outstr = getattr(self, col.name).isoformat()
        else:
            outstr = getattr(self, col.name)             
        return outstr

