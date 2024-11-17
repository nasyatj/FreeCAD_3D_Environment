# Set up FreeCAD environment BEFORE any FreeCAD imports
from setup import setup_freecad_env
setup_freecad_env()

import FreeCAD
import FreeCADGui
import Part
import socket


class CommandProcessor:
    def __init__(self, doc):
        self.doc = doc
        self.objects = {}  # Store created objects
        self.selected = None  # Currently selected object
        self.selected_edges = []  # Store selected edges

        
    def process(self, command):
        """Process a command string and return a result message."""
        words = command.lower().split()
        if not words:
            return "Empty command"
            
        cmd = words[0]
        
        try:
            if cmd == "box":
                return self._create_box(words[1:])
            elif cmd == "sphere":
                return self._create_sphere(words[1:])
            elif cmd == "cylinder":
                return self._create_cylinder(words[1:])
            elif cmd == "select":
                return self._select_object(words[1:])
            elif cmd == "edge":
                return self._select_edge(words[1:])
            elif cmd == "move":
                return self._move_object(words[1:])
            elif cmd == "rotate":
                return self._rotate_object(words[1:])
            elif cmd == "fillet":
                return self._fillet_edges(words[1:])
            elif cmd == "list":
                return self._list_objects()
            elif cmd == "clear":
                return self._clear_all()
            elif cmd == "clearsel":
                return self._clear_selection()
            else:
                return f"Unknown command: {cmd}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _create_box(self, args):
        """Create a box with given dimensions: box length width height"""
        if len(args) != 3:
            return "Usage: box length width height"
        try:
            length, width, height = map(float, args)
            box_name = f"Box_{len(self.objects)}"
            box = self.doc.addObject("Part::Box", box_name)
            box.Label = f"Box {len(self.objects)}"
            box.Length = length
            box.Width = width
            box.Height = height
            self.objects[box_name] = box
            print(f"Created box with name: {box_name}")  # Debug print
            print(f"Current objects: {self.objects}")    # Debug print
            self.doc.recompute()
            return f"Created box {box_name} ({length} x {width} x {height})"
        except ValueError:
            return "Error: Invalid dimensions for box"
    
    def _create_sphere(self, args):
        """Create a sphere with given radius: sphere radius"""
        if len(args) != 1:
            return "Usage: sphere radius"
        try:
            radius = float(args[0])
            sphere = self.doc.addObject("Part::Sphere", f"Sphere_{len(self.objects)}")
            sphere.Radius = radius
            self.objects[sphere.Name] = sphere
            self.doc.recompute()
            return f"Created sphere {sphere.Name} (radius: {radius})"
        except ValueError:
            return "Error: Invalid radius for sphere"
    
    def _create_cylinder(self, args):
        """Create a cylinder: cylinder radius height"""
        if len(args) != 2:
            return "Usage: cylinder radius height"
        try:
            radius, height = map(float, args)
            cylinder = self.doc.addObject("Part::Cylinder", f"Cylinder_{len(self.objects)}")
            cylinder.Radius = radius
            cylinder.Height = height
            self.objects[cylinder.Name] = cylinder
            self.doc.recompute()
            return f"Created cylinder {cylinder.Name} (radius: {radius}, height: {height})"
        except ValueError:
            return "Error: Invalid dimensions for cylinder"
    
    def _list_objects(self):
        """List all created objects"""
        if not self.objects:
            return "No objects created yet"
        result = "Created objects:\n"
        for name, obj in self.objects.items():
            result += f"- {name}\n"
        return result
    
    def _clear_all(self):
        """Remove all objects"""
        for name in list(self.objects.keys()):
            self.doc.removeObject(name)
        self.objects.clear()
        self.doc.recompute()
        return "All objects cleared"

    
    def _select_object(self, args):
        """Select an object by name: select ObjectName"""
        if not args:
            return "Usage: select ObjectName"
        name = args[0]
        
        # Try exact match first
        if name in self.objects:
            obj = self.objects[name]
        else:
            # Try case-insensitive match
            name_lower = name.lower()
            matches = {k: v for k, v in self.objects.items() 
                    if k.lower() == name_lower}
            if not matches:
                return f"No object named {name}"
            obj = next(iter(matches.values()))
            name = next(iter(matches.keys()))
        
        # Clear current selection
        FreeCADGui.Selection.clearSelection()
        # Select the object 
        FreeCADGui.Selection.addSelection(obj)
        self.selected = obj

        # Center view on object
        try:
            view = FreeCADGui.ActiveDocument.ActiveView
            bound_box = obj.Shape.BoundBox
            view.fitAll()  # Fit view to all objects
            # Alternative methods if fitAll() doesn't work:
            # view.viewPosition((0,0,0), 10)  # Reset to default position
            # view.viewAxonometric()  # Set to axonometric view
        except Exception as e:
            print(f"View centering error: {e}")
        
        return f"Selected {name}"
    
    def _select_edge(self, args):
        """Select an edge and view from appropriate side"""
        if len(args) != 2:
            return "Usage: edge ObjectName EdgeNumber"
        
        name, edge_num = args[0], args[1]
        
        try:
            edge_num = int(edge_num)
        except ValueError:
            return "Edge number must be an integer"
        
        # Case insensitive object lookup
        name_lower = name.lower()
        matches = {k: v for k, v in self.objects.items() 
                if k.lower() == name_lower}
        if not matches:
            return f"No object named {name}"
        
        obj = next(iter(matches.values()))
        name = next(iter(matches.keys()))
        
        # Print total edges available
        total_edges = len(obj.Shape.Edges)
        print(f"\nObject {name} has {total_edges} edges")
        
        if edge_num <= 0 or edge_num > total_edges:
            return f"Edge number must be between 1 and {total_edges}"
        
        # Clear current selection
        FreeCADGui.Selection.clearSelection()
        
        # Get edge information
        edge = obj.Shape.Edges[edge_num - 1]
        
        # Debug information about the edge
        print(f"\nEdge {edge_num} analysis:")
        print(f"Edge type: {edge.Curve.__class__.__name__}")
        print(f"Length: {edge.Length:.2f}")
        
        if hasattr(edge.Curve, 'Radius'):
            print(f"Radius: {edge.Curve.Radius:.2f}")
        
        # Get edge geometry
        v1 = edge.Vertexes[0].Point if len(edge.Vertexes) > 0 else None
        v2 = edge.Vertexes[1].Point if len(edge.Vertexes) > 1 else None
        
        if v1 and v2:
            print(f"Start point: ({v1.x:.2f}, {v1.y:.2f}, {v1.z:.2f})")
            print(f"End point: ({v2.x:.2f}, {v2.y:.2f}, {v2.z:.2f})")
            
            # For linear edges
            if isinstance(edge.Curve, Part.Line):
                direction = FreeCAD.Vector(v2.x - v1.x, v2.y - v1.y, v2.z - v1.z).normalize()
                print(f"Direction (linear): ({direction.x:.2f}, {direction.y:.2f}, {direction.z:.2f})")
            
            # For circular edges
            elif isinstance(edge.Curve, Part.Circle):
                center = edge.Curve.Center
                axis = edge.Curve.Axis
                print(f"Center: ({center.x:.2f}, {center.y:.2f}, {center.z:.2f})")
                print(f"Axis: ({axis.x:.2f}, {axis.y:.2f}, {axis.z:.2f})")
        
        # Select the edge
        FreeCADGui.Selection.addSelection(obj, f"Edge{edge_num}")
        self.selected_edges = [(obj, edge_num)]
        
        # Get view object
        view = FreeCADGui.ActiveDocument.ActiveView
        
        # Choose view based on edge type and orientation
        if isinstance(edge.Curve, Part.Circle):
            # For circular edges, view perpendicular to the circle's plane
            axis = edge.Curve.Axis.normalize()
            
            print("\nViewing circular edge...")
            if abs(axis.z) > 0.9:  # Horizontal circle
                print("Horizontal circle - using front view")
                view.viewFront()
            elif abs(axis.x) > 0.9:  # Circle in YZ plane
                print("YZ plane circle - using left view")
                view.viewLeft()
            else:  # Circle in XZ plane
                print("XZ plane circle - using top view")
                view.viewTop()
                
        elif isinstance(edge.Curve, Part.Line):
            # For linear edges, use previous logic for straight edges
            direction = FreeCAD.Vector(v2.x - v1.x, v2.y - v1.y, v2.z - v1.z).normalize()
            print("\nViewing linear edge...")
            
            if abs(direction.z) > 0.9:  # Vertical
                print("Vertical edge - using front view")
                view.viewFront()
            elif abs(direction.y) > 0.9:  # Front-back
                print("Front-back edge - using left view")
                view.viewLeft()
            else:  # Left-right
                print("Left-right edge - using top view")
                view.viewTop()
                
        else:
            # For other edge types, try to get a reasonable view
            print(f"\nUnknown edge type: {edge.Curve.__class__.__name__}")
            print("Using default front view")
            view.viewFront()
        
        # Ensure edge is visible
        view.fitAll()
        
        return f"Selected edge {edge_num} of {name}"
    
    def _select_edge_working(self, args):
        """Select an edge and view from appropriate side"""
        if len(args) != 2:
            return "Usage: edge ObjectName EdgeNumber"
        
        name, edge_num = args[0], args[1]
        
        try:
            edge_num = int(edge_num)
        except ValueError:
            return "Edge number must be an integer"
        
        # Case insensitive object lookup
        name_lower = name.lower()
        matches = {k: v for k, v in self.objects.items() 
                if k.lower() == name_lower}
        if not matches:
            return f"No object named {name}"
        
        obj = next(iter(matches.values()))
        name = next(iter(matches.keys()))
        
        if edge_num <= 0 or edge_num > len(obj.Shape.Edges):
            return f"Edge number must be between 1 and {len(obj.Shape.Edges)}"
        
        # Clear current selection
        FreeCADGui.Selection.clearSelection()
        
        # Get edge information
        edge = obj.Shape.Edges[edge_num - 1]
        v1 = edge.Vertexes[0].Point
        v2 = edge.Vertexes[1].Point
        center = FreeCAD.Vector((v1.x + v2.x)/2, (v1.y + v2.y)/2, (v1.z + v2.z)/2)
        direction = FreeCAD.Vector(v2.x - v1.x, v2.y - v1.y, v2.z - v1.z).normalize()
        
        # Debug prints
        print(f"\nEdge {edge_num} details:")
        print(f"Start point: ({v1.x:.2f}, {v1.y:.2f}, {v1.z:.2f})")
        print(f"End point: ({v2.x:.2f}, {v2.y:.2f}, {v2.z:.2f})")
        print(f"Center: ({center.x:.2f}, {center.y:.2f}, {center.z:.2f})")
        print(f"Direction: ({direction.x:.2f}, {direction.y:.2f}, {direction.z:.2f})")
        
        # Select the edge
        FreeCADGui.Selection.addSelection(obj, f"Edge{edge_num}")
        self.selected_edges = [(obj, edge_num)]
        
        # Get view object
        view = FreeCADGui.ActiveDocument.ActiveView
        
        # Choose view based on edge position and direction
        if abs(direction.z) > 0.9:  # Vertical edges
            if center.y < 5:  # Front vertical edges
                print("Front vertical edge - using front view")
                view.viewFront()
            else:  # Back vertical edges
                print("Back vertical edge - using rear view")
                view.viewRear()
        elif abs(direction.y) > 0.9:  # Front-back edges
            if center.z < 5:  # Bottom front-back edges
                print("Bottom front-back edge - using left view")
                view.viewLeft()
            else:  # Top front-back edges
                print("Top front-back edge - using right view")
                view.viewRight()
        else:  # Left-right edges
            if center.z < 5:  # Bottom left-right edges
                print("Bottom left-right edge - using top view")
                view.viewTop()
            else:  # Top left-right edges
                print("Top left-right edge - using bottom view")
                view.viewBottom()
        
        # Ensure edge is visible
        view.fitAll()
        
        return f"Selected edge {edge_num} of {name}"
    
    def _fillet_edges(self, args):
        """Fillet selected edges: fillet radius"""
        if not self.selected_edges:
            return "No edges selected"
        if len(args) != 1:
            return "Usage: fillet radius"
        
        try:
            radius = float(args[0])
            obj = self.selected_edges[0][0]  # Get the object
            edge_numbers = [edge_num for _, edge_num in self.selected_edges]
            print(f"Filleting object {obj.Name}, edges {edge_numbers}, radius {radius}")  # Debug
            edges = [obj.Shape.Edges[i-1] for i in edge_numbers]
            
            # Create fillet
            filleted = obj.Shape.makeFillet(radius, edges)
            
            # Create new object with fillet
            new_name = f"{obj.Name}_filleted"
            new_obj = self.doc.addObject("Part::Feature", new_name)
            new_obj.Shape = filleted
            self.objects[new_name] = new_obj
            
            # Hide original object
            obj.Visibility = False
            
            self.doc.recompute()
            return f"Created fillet with radius {radius} on {new_name}"
        except ValueError:
            return "Invalid radius for fillet"
        except Exception as e:
            print(f"Fillet error details: {str(e)}")  # Debug
            return f"Fillet failed: {str(e)}"
    
    def _move_object(self, args):
        """Move selected object: move x y z"""
        if not self.selected:
            return "No object selected"
        if len(args) != 3:
            return "Usage: move x y z"
            
        try:
            x, y, z = map(float, args)
            placement = self.selected.Placement
            placement.Base.x += x
            placement.Base.y += y
            placement.Base.z += z
            self.selected.Placement = placement
            self.doc.recompute()
            return f"Moved selected object by ({x}, {y}, {z})"
        except ValueError:
            return "Invalid coordinates for move"
    
    def _rotate_object(self, args):
        """Rotate selected object: rotate angle x y z"""
        if not self.selected:
            return "No object selected"
        if len(args) != 4:
            return "Usage: rotate angle x y z"
            
        try:
            angle, x, y, z = map(float, args)
            rotation_center = self.selected.Shape.BoundBox.Center
            self.selected.Placement.rotate(rotation_center, FreeCAD.Vector(x, y, z), angle)
            self.doc.recompute()
            return f"Rotated selected object by {angle} degrees around ({x}, {y}, z)"
        except ValueError:
            return "Invalid parameters for rotation"
        
    def _clear_selection(self):
        """Clear current selection"""
        FreeCADGui.Selection.clearSelection()
        self.selected = None
        self.selected_edges = []
        return "Selection cleared"

    def _list_objects(self):
        """List all created objects"""
        if not self.objects:
            return "No objects created yet"
        result = "Created objects:\n"
        for name, obj in self.objects.items():
            selected = " (selected)" if obj == self.selected else ""
            result += f"- {name}{selected}\n"
        return result