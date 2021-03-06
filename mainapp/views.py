
from django.shortcuts import render
from django.http import JsonResponse
import json
from . models import Profile, Module
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import redirect


from django.views.decorators.csrf import csrf_exempt



def index(request):



    return render(request, 'index.html')


def loginPage(request):

    if 'firstName' in  request.session:

        return redirect('profile')
    else:
        return render(request, 'login.html')

def signupPage(request):

    return render(request, 'signup.html')

def profile(request):
    
    #create seperate method to initialise user data from session to prevent repeated code

    firstName = request.session['firstName']
    username = request.session['username']
    
    profileData = Profile.objects.get(user_id = str(request.session['userID']))



    return render(request, 'profile.html', ({'username' : firstName,'userEmail': username,
                'userGender': profileData.gender,
                'userDOB': profileData.dateOfBirth}))



def loginProcess(request):
    
    
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username = username, password = password )
    

   

    if user is not None:  
        firstName = user.get_full_name()

      #  request.session.modified = True
        request.session['userID'] = user.id
        request.session['username'] = username
        request.session['password'] = password
        request.session['firstName'] = firstName
        request.session.set_expiry(60 * 60 )
         
            

      
       
        return redirect('profile')
     
    else:
            
        return render(request, 'login.html', {'errorMessage' : 'Incorrect Details'})

    


@csrf_exempt
def signupProcess(request):
    success = False
    if not ('email' in request.POST and 'password' in request.POST):
        pass

    else:
        
        email = request.POST.get('email')
        firstname = request.POST.get('name')
        password = request.POST.get('password')
        moduleList = request.POST.getlist('courses[]')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')

        print(request.POST)
        userInstance = User(username = email ,first_name = firstname, email = email) 
        userInstance.save()
        userInstance.set_password(password)
        userInstance.save()

        

        currentUser = Profile(user = userInstance, gender = gender, dateOfBirth= dob) 
        currentUser.save()
        for selected in moduleList:
            print(selected)
            module = Module.objects.get(name = selected)
            currentUser.modules.add(module)
        
     
        
        return JsonResponse({'success' : True })

def mymatches(request):
    

    return render(request, 'mymatches.html')

def getMatches(request):
    # Return all of the matches potentially, with full list
    # Then we allow filters of where the user can select based on
    # min max age gender

    filter = None
    matchingData = []
    
    currentUserId = request.session['userID']

    currentUserProfile = Profile.objects.get(user_id = currentUserId)
    currentUserModules = currentUserProfile.modules.all()

    if(request.method == 'POST'):
        filter = True
        gender = request.POST.get('gender')
        min = int(request.POST.get('min'))
        max = int(request.POST.get('max'))

        allProfiles = Profile.objects.filter(gender = gender ).exclude(user_id=currentUserId)   

    else :
        allProfiles = Profile.objects.exclude(user_id=currentUserId)   
     
    for profile in allProfiles:
        matchingCount = 0
        profileModules = profile.modules.all()
        
        for module in currentUserModules:
           
            if matchingCount == currentUserModules.count():
               
                break

            if module in profileModules:
                matchingCount+=1
                
       
        if matchingCount > 0:

            age = profile.getAge()  

            if(filter and age<min and age>max):
               
                continue #Skips this iteration


            print(profile.user.first_name)
            percentage = (matchingCount / currentUserModules.count() ) * 100
            firstName = profile.user.first_name
            gender = profile.gender
            modules = []

            for module in currentUserModules.values():
                modules.append(module)
                
            matchingData.append({'firstName': firstName, 'gender' : gender, 'age': age, 'percentage': round(percentage), 'modules':modules })
                #Within list there are python dictionary

                

    return JsonResponse(matchingData, safe = False)

def courses(request):
    
    moduleList = list(Module.objects.values())

    

    return JsonResponse(moduleList, safe=False)
  
