import json
import os
from flask import Flask, Response, flash, request, jsonify,render_template, send_from_directory,url_for,redirect
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_mongoengine import MongoEngine 
from multiprocessing import Value

counter = Value('i', 0)
app = Flask(__name__)


app.config['MONGODB_SETTINGS'] = {'db': 'employee','host': 'localhost','port': 27017
}
db = MongoEngine()
db.init_app(app)

class my(db.Document):
    id =db.StringField(primary_key=True)                                                   
    header = db.StringField(max_length=10)
    img=db.StringField(required="5mb")
    short_Descripation =db.StringField(max_length=20)
    Aartical =db.StringField(max_length=1020)
    
    
    def to_json(self):
        return {"id":self.id,
                "header":self.header,
                "img":self.img,
                "short_Descripation":self.short_Descripation,
                "Aartical":self. Aartical,
                }

#----------------------------------------login--------------------------------------------------   
class login(db.Document):
    email=db.StringField()
    password=db.StringField(max_length=10)

    def to_json(self):
        return {"email":self.email,
                "password":self.password}
#--------------comment----------------------------------------------------------        
class comment(db.Document):
     #id =db.StringField(primary_key=True)
     comment=db.StringField(Foreign_Key=my,max_length=120)
     out=db.IntField(Foreign_Key=my,required=False, min_value=0, default=0)
     like=db.IntField(required=False, min_value=0, default=0)
     #liked = db.relationship(primaryjoin=(my.c.id == id),secondaryjoin=(my.c.id == id))
     
     def to_json(self):
        return {#"id":self.id,
                "comment":self.comment,
                "out":self.out}  
#--------------------------------------------like-----------------------------------------------------
# class Like(db.Document):
#     id = db.StringField(primary_key=True)
#     recipe_id = db.ForeignKeyField(my, backref='comment', lazy_load=False)
class Like(db.Document):
    id = db.StringField(primary_key=True)
    recipe_id =db.StringField(Foreign_Key=my, backref='comment', lazy_load=False)
  #  post_date = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    poster_id =db.StringField(Foreign_Key=my, backref='like', lazy_load=False)
    
    
    
    def to_json(self):
        return {"id":self.id,"recipe_id":self.recipe_id,"poster_id":self.poster_id} 
    
#     def to_json(self):
#         return {"id":self.id,
#                 "recipe_id":self.recipe_id} 
#--------------------------------------------like-----------------------------------------------------
    

     
     
     
@app.route("/")
def index():
    return render_template('index.html')


@app.route('/addrecord', methods=['POST'])
def create_record():
    record = json.loads(request.data)
    user = my(id=record["id"],
                 header=record["header"],
                 img=record["img"],
                 short_Descripation=record["short_Descripation"],
                 Aartical=record["Aartical"])
    user.save()
    response = {
                'status': 'success',
                'message': 'record add successfully',
                'data':[user]
            }
    
    return jsonify(user.to_json(),response)



@app.route("/like4/<int:id>", methods=['GET'])
@jwt_required

def like4(id):
    current_user = get_jwt_identity()
    recipe_id = my.get(id)
    like = Like.select().where((my.poster_id == current_user) & (my.id == id))
    if not my.select().where(my.id == id).exists():
        return jsonify('Recipe ID does not Exist'), 404
    elif like:
            like = Like.delete().where((my.poster_id == current_user) & (my.id == id))
            like.execute()
    else:
        like = Like.create(recipe_id = recipe_id , poster_id=current_user )
        return jsonify(f'You have liked the recipe with ID:  {recipe_id}'), 200




@app.route('/like1/<id>', methods=['POST'])
def like(id):
    my.objects.get(id=id) 
    with counter.get_lock():
        counter.value += 1
       # counter.save()
        out = counter.value
    
        outt=comment(out=out)
      
        outt.save()
        
    return jsonify(count=out) 



@app.route('/dislike/<id>', methods=['POST'])
def dislike(id):
    my.objects.get(id=id) 
 
    with counter.get_lock():
        counter.value -= 1
       # counter.save()
        out = counter.value
        #my.save()  
    return jsonify(count=out) 






@app.route("/like2/<id>", methods=['POST'])
#@login_required
def like5(id):
    my.objects.get(id=id)                        #post=
    #counter=Value('i', 0)
    with counter.get_lock():
        counter.value += 1
        oute = counter.value

    #comment.count()
    p=comment(like=oute)
    p.save()
    flash('Post has been liked')
    return jsonify(oute)



@app.route("/like/<id>",methods=["POST"])
def like_view(id):
    #my.objects.get(id=id)
    record=json.loads(request.data)
    my.objects.get(id=id)
    with counter.get_lock():
        counter.value += 1
        oute = counter.value
    user=comment(oute)
    #user=comment(out=record[oute])                  #id=record["id"]
    user.save()
    return jsonify(user.to_json())






@app.route("/login",methods=["POST"])
def log():
    record=json.loads(request.data)
    user=login(email=record["email"],
               password=record["password"])
    user.save()
    response = {
                'status': 'success',
                'message': 'login successfully',
                'data':[user]
            }
    return jsonify(user.to_json(),response)


@app.route('/show',methods=["GET"])
def get():
    user = my.objects().to_json()
    return Response(user,mimetype="application/json")    



@app.route("/comment/<id>",methods=["POST"])
def commentview(id):
    my.objects.get(id=id)                 #.update(**record)
    record=json.loads(request.data)
    user=comment(comment=record["comment"]) #id=record["id"],
    user.save()
    # response = {
    #             'status': 'success',
    #             'message': 'comment successfully',
    #             'data':[]
    #         }
    return jsonify(user.to_json())                           #,response)








@app.route("/edit/<id>",methods=["PUT"])
def editview(id):
   
    record=json.loads(request.data)
    #body = request.to_json()
    my.objects.get(id=id).update(**record)

    
    return jsonify({'status': 'success','message': ' edit successfully',})                #   user.to_json(),response)





@app.route("/delete/<id>",methods=["DELETE"])
def deleteview(id):
    my.objects.get(id=id).delete()
    
    return jsonify({'status': 'success','message': 'delete successfully'})                #  db.to_json(),response,200)

    
    
  
 

#-------------------------------------------upload img ------------------------------------------------------------------------    
    

APP_ROOT = os.path.dirname(os.path.abspath(__file__))



@app.route("/index1")
def index1():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload():
    target = os.path.join(APP_ROOT, 'images/')
    if not os.path.isdir(target):
            os.mkdir(target)
    else:
        print("Couldn't create upload directory: {}".format(target))

    for upload in request.files.getlist("file"):
        print("LOG: filename: {}".format(upload.filename))
        filename = upload.filename
        destination = "/".join([target, filename])
        print ("LOG: Accept incoming file:", filename)
        print ("LOG: Save it to:", destination)
        upload.save(destination)

    return render_template("display.html", image_name=filename)

@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)






if __name__=="__main__":
    app.run(debug=True)

