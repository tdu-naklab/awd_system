import numpy as np
import cv2

cap = cv2.VideoCapture(0)
lower_red = np.array([0,0,180])
upper_red = np.array([50,50,255])
#height = 480
#width = 640
while(True):
	ret,frame = cap.read()
	b,g,r = cv2.split(frame)
	print('r=' +str(r),'g=' +str(g),'b=' +str(b))
	mask = (r > 180) & (g < 50) & (b < 50)			#detection red
	mask_red = cv2.inRange(frame,lower_red,upper_red)	#mask red
	m = cv2.moments(mask_red)
	if m['m00'] != 0:
		x = int(m['m10'] // m['m00'])
		y = int(m['m01'] // m['m00'])
	
	if mask.any():
		frame = cv2.line(frame,(x,y-100),(x,y+100),(0,255,0),1)
	cv2.imshow('frame',frame)
	k = cv2.waitKey(25) & 0xFF
	if k == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()




