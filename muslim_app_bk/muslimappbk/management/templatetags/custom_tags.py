#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Callmethod - TemplateTag
    
        
        {% callmethod hotel.room_price_for_night night_date="2018-01-02" room_type=room_type_context_var %}
            -equals-
        hotel.room_price_for_night(night_date="2018-01-02", room_type="standard") #Assuming "standard" is the value of room_type_context_var
        
    
    Django doesn't allow calling a method with arguments in the template to ensure good separation of 
    design and code logic.
    
    However, sometimes you will be in situations where it is more maintainable to pass an argument
    to a method in the template than build an iterable (with the values already resolved) in a view.
    
    Furthermore, Django doesn't strictly follow its own ideology: the {% url "url:scheme" arg, kwarg=var %}
    templatetag readily accepts variables as parameters!!
    
    This template tag allows you to call a method on an object, with the specified arguments.
    
    Usage:
    
        {% callmethod object_var.method_name "arg1_is_a_string" arg2_is_a_var kwarg1="a string" kwarg2=another_contect_variable %}
    
    e.g.
        {% callmethod hotel.room_price_for_night date="2018-01-02" room_type="standard" %}
        {% callmethod hotel.get_booking_tsandcs "standard" %}
        
    NB: If for whatever reason you've ended up with a template context variable with the same name as the method you want to
    call on your object, you will need to force the template tag to regard that method as a string by putting it in quotes:
    
        {# Ensure we call hotel.room_price_for_night() even though there's a template var called {{ room_price_for_night }}! #}
        {% callmethod hotel."room_price_for_night" date="2018-01-02" room_type="standard" %}
    
    
    @author: Dr Michael J T Brooks
    @version: 2018-01-05
    @copyright: Onley Group 2018 (Onley Technical Consulting Ltd) http://www.onleygroup.com
    @license: MIT (use as you wish, AS IS, no warranty on performance, no liability for losses, please retain the notice)
    
    @write_code_GET_PAID: Want to work from home as a Django developer? Earn GBP30-GBP50 per hour ($40-$70) depending on experience
                          for helping Onley Group develop its clients' Django-based web apps.
                          E-mail your CV and some sample portfolio code to: freelance_developers[at]onleygroup.com
    
    Copyright 2018 Onley Group

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
    documentation files (the "Software"), to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice, credits, and this permission notice shall be included in all copies or 
    substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED 
    TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
    CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
    DEALINGS IN THE SOFTWARE.

"""
from __future__ import unicode_literals
import re
from django.template import Library, TemplateSyntaxError, Node
from django.utils.encoding import smart_text

register = Library()


#Regex for keyword arguments
ARG_KWARG_RE = re.compile(r"(?:(\w+)=)?(.+)")


class CallMethodNode(Node):
    """
    Renders the relevant value of a {% callmethod %} template tag
    """
    def __init__(self, object_name, method_name, args=None, kwargs=None, asvar=False):
        self.object_name_resolver = object_name
        self.method_name_resolver = method_name
        self.args_resolvers = args or []
        self.kwargs_resolvers = kwargs or {}
        self.asvar = asvar
    
    def render(self, context):
        """
        Actually renders the node based upon the context
        
        @param context: {} The template context dict
        """
        #Turn our resolvers into actual values:
        try:
            object_obj = self.object_name_resolver.resolve(context)
        except AttributeError: #Happens if a string was passed in as the object name. Try to rescue this and treat as a var:
            object_obj = context.get(self.object_name_resolver, None)
        method_name = self.method_name_resolver.resolve(context) or str(self.method_name_resolver) #Can resolve as variable, but will also resolve as a string. Put in "inverted commas" to force string resolution
        if not object_obj or not method_name:
            raise TemplateSyntaxError("{{%% callmethod object_name.method_name %%}} cannot make sense of the resolved values for object_name.method_name '{object_name}.{method_name}'".format(object_name=self.object_name_resolver, method_name=self.method_name_resolver))
        #Resolve the args
        args = []
        for arg_resolver in self.args_resolvers:
            arg = arg_resolver.resolve(context)
            args.append(arg)
        #Resolve the kwargs
        kwargs = {}
        for k_raw, v_resolver in self.kwargs_resolvers.items():
            k = smart_text(k_raw,'ascii')
            v = v_resolver.resolve(context)
            kwargs[k]=v
        
        #Now try to call the method on the object
        try:
            output = getattr(object_obj, method_name)(*args, **kwargs)
        except Exception as e: #Fail silently, but tell the console:
            print("\033[91m{err_type} from {{%% callmethod <{obj_name}>.{method_name}() %%}}: {err_msg}\033[0m".format(err_type=e.__class__.__name__, obj_name=object_obj, method_name=method_name, err_msg=e))
            output = ""
        
        #Set to context variable if a context variable:
        if self.asvar:
            context[self.asvar] = output #NB: context is a dict, which is mutable :-)
            return ""
        return output #Otherwise return output (i.e. render this string into the page) 


@register.tag
def callmethod(parser, token):
    """
    Call the specified method, on the specified object, with the specified arguments and kwargs
    
        NB: parser.compile_filter(var):
            Takes the var name as a string, processes any filters that
            have been used, then tries to resolve into a variable.
    """
    #Check syntax:
    parts = token.split_contents() #Splits apart by space (but preserves spaces in quotes)
    if len(parts)<2:
        raise TemplateSyntaxError("{{%% callmethod %%}} takes at least one argument (the object.its_method) e.g. {%% callmethod my_object.the_method arg1 kwarg1=a_var %%}")
    
    #Defaults
    object_name = ""
    method_name = ""
    args = []
    kwargs = {}
    
    #Get our object and method:
    try:
        obj_method_parts = parts[1].split(".")
        object_name = obj_method_parts[0]
        method_name = obj_method_parts[1]
    except (IndexError, AttributeError):
        raise TemplateSyntaxError("{{%% callmethod %%}} should have its object and method specified using dot notation: e.g. {%% callmethod my_object.the_method arg1 kwarg1=a_var %%}")
    try: #Resolve any filters used to build the name
        object_name = parser.compile_filter(object_name)
        method_name = parser.compile_filter(method_name)
    except TemplateSyntaxError as e:
        print("WARNING {{%% callmethod {obj_name}.{method_name} %%}} cannot make sense of '{obj_name}'".format(obj_name=object_name, method_name=method_name))
    
    #See if we want to dump this output into a template variable
    asvar = None
    if len(parts) >= 2 and parts[-2] == 'as':
        asvar = parts[-1] #The context variable we are creating to store the resolved value
        parts = parts[:-2] #Chew off the last two words as we've dealt with them!
    
    #Resolve our kwargs:
    args_and_kwargs = parts[2:]
    if len(args_and_kwargs):
        for arg_or_kwarg in args_and_kwargs:
            match = ARG_KWARG_RE.match(arg_or_kwarg)
            if not match:
                raise TemplateSyntaxError("{{%% callmethod {obj_name}.{method_name} {arg_or_kwarg} %%}} cannot make sense of argument / kwarg '{arg_or_kwarg}'".format(obj_name=object_name, method_name=method_name, arg_or_kwarg=arg_or_kwarg))
            name, value = match.groups()
            resolved_value = parser.compile_filter(value)
            if name:
                kwargs[name] = resolved_value
            else:
                args.append(resolved_value)
    
    #Hand our vars over to our rendering node:
    return CallMethodNode(object_name, method_name, args, kwargs, asvar)

@register.simple_tag(name="verbose_name")
def verbose_name_tag(obj, field_name):
    return obj._meta.get_field(field_name).verbose_name

@register.filter(name="verbose_name")
def verbose_name_filter(obj, field_name):
    return obj._meta.get_field(field_name).verbose_name
