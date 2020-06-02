import pygame
from vector import *
import math
import colorsys

pygame.init()

win_width = 800
win_height = 500
scale_factor = 10
win = pygame.display.set_mode((win_width,win_height))

l_border = -40
r_border = 40

# 3D:
zoom = 1000
dot_radius = 3

light_vec = (1,1,1)
camera_vec = (0,0,100)

pos_x = win_width/2
pos_y = win_height/2

world_rot = (0,0,0,1)

################################################################################ Quaternions math
def quaternion_mul(q1, q2):
	x =  q1[0] * q2[3] + q1[1] * q2[2] - q1[2] * q2[1] + q1[3] * q2[0]
	y = -q1[0] * q2[2] + q1[1] * q2[3] + q1[2] * q2[0] + q1[3] * q2[1]
	z =  q1[0] * q2[1] - q1[1] * q2[0] + q1[2] * q2[3] + q1[3] * q2[2]
	w = -q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2] + q1[3] * q2[3]
	return (x,y,z,w)
	
def quaternion_mul_unit(q1, q2):
	prod = quaternion_mul(q1, q2)
	size = math.sqrt(prod[0]**2 + prod[1]**2 + prod[2]**2 + prod[3]**2)
	x = prod[0]/size
	y = prod[1]/size
	z = prod[2]/size
	w = prod[3]/size
	return (x,y,z,w)

def quaternion_con_mul(vec, q1):
	q2 = (-q1[0], -q1[1], -q1[2], q1[3])
	vec_q = (vec[0], vec[1], vec[2], 0)
	a1 = quaternion_mul(q1, vec_q)
	a2 = quaternion_mul(a1, q2)
	return (a2[0], a2[1], a2[2])

def normalize_quaternion(q):
	size = math.sqrt(q[0]**2 + q[1]**2 + q[2]**2 + q[3]**2)
	if size == 0:
		return (0,0,0,0)
	x = q[0]/size
	y = q[1]/size
	z = q[2]/size
	w = q[3]/size
	return (x,y,z,w)

def normalize_vec(q):
	size = math.sqrt(q[0]**2 + q[1]**2 + q[2]**2)
	if size == 0:
		return (0,0,0)
	x = q[0]/size
	y = q[1]/size
	z = q[2]/size
	return (x,y,z)

def axis_from_quaternion(q):
	axis = normalize_vec((q[0], q[1], q[2]))
	return axis

def quaternion_from_axis_angle(axis, angle):
	qx = axis[0] * math.sin(angle/2)
	qy = axis[1] * math.sin(angle/2)
	qz = axis[2] * math.sin(angle/2)
	qw = math.cos(angle/2)
	return (qx, qy, qz, qw)
################################################################################ Transformations
def param(x,y,z):
	vec = quaternion_con_mul((x,y,z), world_rot)
	return ((zoom * vec[0])/(70-vec[2]) + pos_x,-( (zoom * vec[1])/(70-vec[2]) ) + pos_y)

def smap(value,a,b,c,d,clamped = False):
	ans = (value - a)/(b - a) * (d - c) + c
	if clamped:
		if ans > d:
			return d
		if ans < c:
			return c
	return (value - a)/(b - a) * (d - c) + c

def draw_point(pos, color):
	pos_param = (int(param(pos[0], pos[1], pos[2])[0]), int(param(pos[0], pos[1], pos[2])[1]))
	pygame.draw.circle(win, color, pos_param , dot_radius)

def draw_poly(p1,p2,p3,p4):
	vec1 = (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])
	vec2 = (p4[0] - p1[0], p4[1] - p1[1], p4[2] - p1[2])
	normal = (vec1[1]*vec2[2] - vec1[2]*vec2[1], -(vec1[0]*vec2[2] - vec1[2]*vec2[0]), vec1[0]*vec2[1] - vec1[1]*vec2[0])
	product = normal[0]*light_vec[0] + normal[1]*light_vec[1] + normal[2]*light_vec[2]
	
	color = hsv2rgb(60,smap(product,3,0,0,100,True),smap(product,0,3,50,100,True))
	pygame.draw.polygon(win, color, [param(p1[0],p1[1],p1[2]),param(p2[0],p2[1],p2[2]),param(p3[0],p3[1],p3[2]),param(p4[0],p4[1],p4[2])])

def draw_path(list, color):
	if len(list) == 1:
		list.append(list[0])
	if len(list) == 0:
		return
	lines_list = []
	for pos in list:
		pos_param = (int(param(pos[0], pos[1], pos[2])[0]), int(param(pos[0], pos[1], pos[2])[1]))
		lines_list.append(pos_param)
	pygame.draw.lines(win, color, False, lines_list)
	
def draw_axis():
	draw_path([(0,0,0), (5,0,0)], (255,0,0))
	draw_path([(0,0,0), (0,5,0)], (0,255,0))
	draw_path([(0,0,0), (0,0,5)], (0,0,255))

def hsv2rgb(h,s,v):
	h/=100
	s/=100
	v/=100
	return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))
	
def dist2view(point):
	return math.sqrt((point.x - cam_vec[0])**2 + (point.y - cam_vec[1])**2 + (point.z - cam_vec[2])**2)
	
def mouse_event_check():
	global mouse_hold, mouse_speed, zoom
	if event.type == pygame.MOUSEMOTION:
		mouse_speed = event.rel
	if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
		mouse_hold = True
	if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
		mouse_hold = False
	if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
		zoom += 100
	if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
		if zoom > 0:
			zoom -= 100
			
def world_position_keys_check():
	global pos_x, pos_y
	if keys[pygame.K_a]:
		pos_x -= 1
	if keys[pygame.K_d]:
		pos_x += 1
	if keys[pygame.K_w]:
		pos_y -= 1
	if keys[pygame.K_s]:
		pos_y += 1

def world_rotation_keys_check():
	global world_rot
	if keys[pygame.K_KP9]:
		world_rot = quaternion_mul(quaternion_from_axis_angle((1,0,0), angle_offset), world_rot)
	if keys[pygame.K_KP7]:
		world_rot = quaternion_mul(quaternion_from_axis_angle((1,0,0), -angle_offset), world_rot)
	if keys[pygame.K_KP6]:
		world_rot = quaternion_mul(quaternion_from_axis_angle((0,1,0), angle_offset), world_rot)
	if keys[pygame.K_KP4]:
		world_rot = quaternion_mul(quaternion_from_axis_angle((0,1,0), -angle_offset), world_rot)
	if keys[pygame.K_KP3]:
		world_rot = quaternion_mul(quaternion_from_axis_angle((0,0,1), angle_offset), world_rot)
	if keys[pygame.K_KP1]:
		world_rot = quaternion_mul(quaternion_from_axis_angle((0,0,1), -angle_offset), world_rot)
	if keys[pygame.K_KP_PERIOD]:
		world_rot = (0,0,0,1)

def mouse_hold_check():
	global mouse_hold, world_rot, mouse_speed
	if mouse_hold:
		offset_x = mouse_speed[0]
		offset_y = mouse_speed[1]
		
		world_rot = quaternion_mul(quaternion_from_axis_angle(axis_z, offset_x*0.01), world_rot)
		world_rot = quaternion_mul(quaternion_from_axis_angle((1,0,0), offset_y*0.005), world_rot)
	else:
		mouse_speed = (0,0)
		
def update_vecs():
	global cam_vec, axis_z
	cam_vec = quaternion_con_mul(camera_vec, (-world_rot[0], -world_rot[1], -world_rot[2], world_rot[3]))
	axis_z = quaternion_con_mul((0,0,1), world_rot)

################################################################################ Point

class Point:
	_reg = []
	def __init__(self, x, y, z, g):
		self._reg.append(self)
		self.x = x
		self.y = y
		self.z = z
		self.x_next = None
		self.x_prev = None
		self.y_next = None
		self.y_prev = None
		
		self.acc = 0
		self.vel = 0
	def draw(self):
		
		#by polygons:
		if self.x_next == None or self.y_next == None:
			return
		p1 = (self.x, self.y, self.z)
		p2 = (self.x_next.x, self.x_next.y, self.x_next.z)
		p3 = (self.x_next.y_next.x, self.x_next.y_next.y, self.x_next.y_next.z)
		p4 = (self.y_next.x, self.y_next.y, self.y_next.z)

		draw_poly(p1,p2,p3,p4)
		#by points:
		# if self.x_prev == None or self.x_next == None or self.y_next == None or self.y_prev == None:
			# draw_point((self.x, self.y, self.z), (255,255,0))
		# else:
			# draw_point((self.x, self.y, self.z), hsv2rgb(0,smap(self.z,-1,1,0,100,True),100))
		
	def calc(self):
		if self.x_next == None:
			self.z = right(t, self.x, self.y)
			self.acc = 0
			self.vel = 0
			return
		if self.x_prev == None:
			self.z = left(t, self.x, self.y)
			self.acc = 0
			self.vel = 0
			return
		if self.y_prev == None:
			self.z = down(t, self.x, self.y)
			self.acc = 0
			self.vel = 0
			return
		if self.y_next == None:
			self.z = up(t, self.x, self.y)
			self.acc = 0
			self.vel = 0
			return
		dx = self.x_next.x - self.x
		dy = self.y_next.y - self.y
		uxx = (self.x_next.z - 2 * self.z + self.x_prev.z) / dx**2
		uyy = (self.y_next.z - 2 * self.z + self.y_prev.z) / dy**2
		
		self.acc = 0.1 *( uxx + uyy )
	
	def step(self):
		self.vel += self.acc
		#self.vel *= 0.999
		self.z += self.vel
	def __str__(self):
		string = "("
		string += str(self.x)
		string += ","
		string += str(self.y)
		string += ")"
		return string
	def __repr__(self):
		return str(self)
		
################################################################################ Initial conditions
def f(x,y):
	#return 0
	#return 5 if x**2 + y**2 < 100 else 0
	return 10 * math.exp(-0.05*(x)**2 -0.05*(y)**2)
def g(x,y):
	return 0
def right(t,x,y):
	#return 5*math.exp(-0.02*(y)**2)*math.sin(t)
	return 0
	return t % 20 
def left(t,x,y):
	#return 5*math.exp(-0.02*(y)**2)*math.sin(t)
	return 0
def up(t,x,y):
	return 0
	return 5*math.exp(-0.02*(x)**2)*math.sin(t)
	##return 0
def down(t,x,y):
	#return 5*math.exp(-0.02*(x)**2)*math.sin(t)
	return 0

# Create points:
square = 40
list = []
for x in range(-square//2,square//2):
	list_row = []
	for y in range(-square//2,square//2):
		p = Point(x,y,f(x,y),g(x,y))
		list_row.append(p)
	list.append(list_row)

for x in range(square):
	i = x - square//2
	for y in range(square):
		j = y - square//2

		if i == -square//2 and j == -square//2:
			list[x][y].x_next = list[x+1][y]
			list[x][y].y_next = list[x][y+1]
		elif i == -square//2 and j == square//2 - 1:
			list[x][y].x_next = list[x+1][y]
			list[x][y].y_prev = list[x][y-1]
		elif i == square//2 - 1 and j == -square//2:
			list[x][y].x_prev = list[x-1][y]
			list[x][y].y_next = list[x][y+1]
		elif i == square//2 - 1 and j == square//2 - 1:
			list[x][y].x_prev = list[x-1][y]
			list[x][y].y_prev = list[x][y-1]
		elif i == -square//2:
			list[x][y].x_next = list[x+1][y]
			list[x][y].y_next = list[x][y+1]
			list[x][y].y_prev = list[x][y-1]
		elif i == square//2 - 1:
			list[x][y].x_prev = list[x-1][y]
			list[x][y].y_prev = list[x][y-1]
			list[x][y].y_next = list[x][y+1]
		elif j == -square//2:
			list[x][y].y_next = list[x][y+1]
			list[x][y].x_next = list[x+1][y]
			list[x][y].x_prev = list[x-1][y]
		elif j == square//2 - 1:
			list[x][y].y_prev = list[x][y-1]
			list[x][y].x_prev = list[x-1][y]
			list[x][y].x_next = list[x+1][y]
		else:
			list[x][y].x_next = list[x+1][y]
			list[x][y].x_prev = list[x-1][y]
			list[x][y].y_next = list[x][y+1]
			list[x][y].y_prev = list[x][y-1]

t = 0
dt = 0.1

time = 0
cycle = 1
cam_vec = (0,0,0)
axis_z = (0,0,0)
mouse_hold = False
angle_offset = 0.1
mouse_speed = (0,0)
#initial rotation:
world_rot = quaternion_mul_unit(quaternion_from_axis_angle((1,0,0), -2*math.pi/6), world_rot)

################################################################################ Main Loop
run = True
while run:
	pygame.time.delay(0)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		mouse_event_check()
		# if event.type == pygame.KEYDOWN:
			# if event.key == pygame.K_KP_MINUS:
				# if dot_radius != 1:
					# dot_radius -= 1
			# if event.key == pygame.K_KP_PLUS:
				# dot_radius += 1
	keys = pygame.key.get_pressed()
	if keys[pygame.K_ESCAPE]:
		run = False
	####################### World position keys
	world_position_keys_check()
	####################### World rotations keys
	world_rotation_keys_check()
	
	if keys[pygame.K_r]:#reset wave
		for p in Point._reg:
			p.z = f(p.x, p.y)
			p.acc = 0
			p.vel = 0
			t = 0
	mouse_hold_check()
	
	#steps
	win.fill((0,0,0))
	draw_axis()
	
	update_vecs()
	
	for p in Point._reg:
		p.calc()
	for p in Point._reg:
		p.step()
	Point._reg.sort(key = dist2view, reverse = True)
	for p in Point._reg:
		p.draw()
	
	#draw_path([(0,0,0), cam_vec], (255,255,0))
	
	t += dt

	#update game
	time += 1
	if time % cycle == 0:
		pygame.display.update() 

pygame.quit()















