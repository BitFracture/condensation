#! /usr/bin/env python3
"""Administrtative code for the data layer.

Running this module will regenerate the database.

static methods:
    declareSchema - declare the schema
    dropSchema - drops the schema
    populate - populates the database with data
"""
from schema import _Base, User, File, Thread, Comment
from session import SessionManager
from sqlalchemy import *
from sqlalchemy.engine import reflection
from sqlalchemy.schema import Table, DropTable, DropConstraint



def declareSchema(engine):
    """Declares the schema."""
    _Base.metadata.create_all(bind=engine)

    
def dropSchema(engine):
    """Drops the schema."""

    # From http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything
    inspector = reflection.Inspector.from_engine(engine)
    metadata = MetaData()
    
    tbs = []
    all_fks = []
    
    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append( ForeignKeyConstraint((),(),name=fk['name']))
        t = Table(table_name,metadata,*fks)
        tbs.append(t)
        all_fks.extend(fks)
    
    for fkc in all_fks:
        engine.execute(DropConstraint(fkc))
    
    for table in tbs:
        engine.execute(DropTable(table))


def populate(session):
    """Populates the database with data."""
    values = {}
    values["name1"] = "Bilbo Baggins"
    values["name2"] = "Frodo Baggins"
    values["name3"] = "Gollum"
    values["uid1"] = "107225912631866552739"
    values["uid2"] = "107225922631866552739"
    values["uid3"] = "107226212631866552739"
    values["fname1"] = "There and back again"
    values["fname2"] = "The lusty argonian maid"
    values["fname3"] = "Pugilism Illustrated"
    values["url1"] = "www.joes-crematorium.com"
    values["url2"] = "www.parrot-muzzles-r-us.com"
    values["url3"] = "www.tire-photos.com"
    values["heading1"] = "420 yolo swag 4 real"
    values["heading2"] = "shitpost"
    values["heading3"] = "I ate a melon, rind and all. AMA"
    values["body1"] = "Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit..."
    values["body2"] = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut eu lacus nibh. Vestibulum neque leo, viverra nec eros sit amet, vehicula feugiat ligula. Quisque maximus, neque in gravida ultricies, nunc mauris pretium orci, ut porta augue purus in nulla. Integer non aliquet risus. Nam ligula urna, euismod scelerisque metus eu, malesuada suscipit lorem. Proin ullamcorper lorem quis rhoncus iaculis. Integer sollicitudin sed lectus quis faucibus.
        
    Morbi est ligula, bibendum quis faucibus vitae, tempus nec ante. In sit amet odio maximus, blandit leo id, vulputate tortor. Nunc non laoreet lorem, ut finibus lorem. In vulputate porta nunc vitae maximus. In hac habitasse platea dictumst. Donec ex neque, malesuada vestibulum sem quis, pharetra varius ligula. Quisque nec lectus urna. Nulla facilisi. In in turpis odio.
        
    Etiam ullamcorper leo eros, in placerat risus posuere nec. Morbi elementum sapien a quam finibus sollicitudin. Suspendisse id viverra dui, sed vestibulum nunc. Nunc tempor sed ante metus."""
    values["body3"] = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin a semper nunc. Quisque bibendum egestas auctor. Phasellus varius, nunc in porttitor tristique, tortor quam vestibulum turpis, a porta tellus enim ac enim. In at massa in mauris placerat semper. Curabitur bibendum ut odio nec cursus. Suspendisse non ipsum sed velit sollicitudin pulvinar at nec orci. Donec nibh orci, porttitor at dignissim ut, suscipit nec justo.
       
    Suspendisse lacinia nec risus sit amet convallis. Proin malesuada dapibus tellus in venenatis. Duis ac ex vehicula, facilisis sem ac, pulvinar elit. Suspendisse porttitor ex tincidunt sagittis aliquam. Etiam at elementum dui. Suspendisse pulvinar magna purus, a sagittis nulla cursus gravida. Donec lacinia risus orci. Nullam placerat tortor at arcu semper, eu bibendum felis molestie.
        
        Proin eleifend odio neque, in lobortis nunc posuere nec. Nunc a lorem et tortor suscipit semper eget nec mauris. Pellentesque viverra elit eget justo posuere, ut interdum justo tristique. Vivamus semper arcu sapien, sed porttitor arcu mollis quis. Duis pretium mauris velit. Mauris viverra velit nec fermentum tristique. Maecenas venenatis, elit id rutrum mollis, velit mi iaculis dui, blandit pulvinar nisl erat quis orci. Maecenas fermentum id tortor id tincidunt. Morbi pulvinar nunc vel tempor sagittis. Mauris porttitor velit ut arcu malesuada, at efficitur velit porttitor. Etiam sed nulla quam. Praesent eleifend mollis turpis at interdum. Nulla dignissim porttitor gravida. Praesent in velit facilisis, tempus ante et, feugiat lorem. In non elit eget eros gravida rutrum. Aenean mattis quis ante quis bibendum.
        
    Pellentesque sed lectus efficitur, rutrum mauris non, tincidunt urna. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Aenean varius nisi et justo euismod tristique vitae et ante. Aenean dolor nunc, suscipit sit amet lectus varius, hendrerit volutpat justo. Vestibulum nibh nisl, malesuada ut dolor ac, consequat commodo ante. Nam mattis aliquam mattis. Vestibulum non porta sem. Ut tristique pretium libero sed semper. Nulla dictum leo sem, quis sodales quam sollicitudin elementum. Interdum et malesuada fames ac ante ipsum primis in faucibus. Curabitur sit amet blandit metus. Curabitur elementum fringilla ligula, ut egestas massa molestie nec. Etiam semper eros sit amet rhoncus rhoncus. Aliquam id metus eu tellus volutpat venenatis id ac ligula.
        
    Vestibulum pellentesque laoreet consequat. Etiam imperdiet tortor sem, at vestibulum nisi maximus in. Sed sed sodales justo. Aliquam luctus, diam non tempor lacinia, nisl justo iaculis nulla, et pulvinar augue ipsum vitae est. Cras pulvinar dolor eget ullamcorper venenatis. Quisque eu sapien elementum, porta erat at, volutpat sapien. In sit amet ex aliquam, aliquam erat quis, iaculis ex. In volutpat erat hendrerit libero posuere, at mattis dolor congue. Morbi mollis nulla nisi, non interdum odio dignissim eget. Etiam convallis metus non dui posuere tristique.
        
    In viverra dictum elit, at rhoncus lectus elementum eu. Quisque ut leo non eros sollicitudin tristique et quis tellus. Quisque pharetra tellus ac dolor ultrices ultrices. Nulla semper arcu quis ex sodales, pulvinar lacinia nisl mollis. Nulla consectetur, erat pretium ultricies lobortis, justo arcu commodo eros, nec vehicula nisi mauris quis urna. Donec nec massa bibendum, mollis odio nec, dapibus nisi. Ut a dui sit amet nibh iaculis dignissim. Ut sem eros, accumsan in porttitor malesuada, pulvinar et urna. Etiam purus tortor, facilisis nec feugiat ut, pellentesque et lectus. Proin sit amet sodales justo. Integer egestas ac diam nec aliquet. Nullam vitae leo metus.
        
    Pellentesque laoreet porttitor quam vitae dictum. Quisque ultrices urna id sapien fermentum, non pellentesque tellus tincidunt. Mauris porttitor tellus vel elit congue pulvinar. Curabitur non maximus purus, eu aliquam massa. Pellentesque cursus aliquam mi at facilisis. In purus mauris, mattis et tortor eu, faucibus hendrerit diam. Sed at aliquet lectus, non aliquam purus.
        
    Donec sit amet elit odio. Nunc ornare, mi eu faucibus sagittis, velit mi lobortis orci, laoreet dapibus risus orci ac leo. Nam posuere sollicitudin lorem sed semper. Donec malesuada rhoncus sem, sit amet sodales mauris. Aenean arcu turpis, dignissim id enim ac, vehicula maximus lacus. Etiam pharetra ligula et est pharetra rhoncus. Fusce vitae ex fermentum, scelerisque dolor ac, sagittis ex. Praesent ipsum magna, congue gravida mauris vel, pellentesque congue enim. Phasellus nec hendrerit velit.
        
    Quisque hendrerit commodo placerat. Vestibulum suscipit augue eget maximus laoreet. Sed et ante id leo scelerisque malesuada non sit amet dolor. Nam pharetra rhoncus dui, in ullamcorper ante sodales vel. Sed placerat fringilla turpis, a mattis massa posuere sit amet. Vestibulum a pulvinar dolor. Cras magna orci, consequat id condimentum sed, consectetur eget est. Nullam vitae hendrerit nisi. Donec ultrices, ipsum et blandit imperdiet, turpis risus dignissim ipsum, vitae dignissim ligula velit id nisl. Nullam condimentum placerat commodo. Sed ut eleifend mauris. Nunc sed sollicitudin massa. Pellentesque in dolor id metus aliquam tincidunt non et lorem. Sed id lobortis leo. Praesent euismod eros posuere turpis tristique accumsan. Cras gravida velit vel lacus mollis fermentum.
        
    Donec porta eu lacus sit amet pellentesque. Aenean accumsan rutrum ultricies. Proin est libero, suscipit sit amet condimentum sit amet, facilisis et orci. Proin finibus consequat augue. Pellentesque pretium ex et quam imperdiet, vitae congue nibh hendrerit. Mauris justo enim, dapibus ut diam in, fringilla vehicula metus. Mauris tristique turpis ornare nunc laoreet, quis varius sem blandit. Sed at varius libero, a viverra diam. Pellentesque condimentum eget urna id condimentum. Etiam vehicula pretium tellus ut fermentum. In sodales tortor et neque euismod, at pulvinar nisl scelerisque. In odio nulla, congue vel sodales nec, egestas quis odio. Pellentesque scelerisque, dui a venenatis gravida, sem eros tempus nulla, vitae venenatis neque nulla ac ligula. Suspendisse ligula tortor, consequat non vehicula sed, commodo quis elit. Maecenas congue nunc nec justo convallis, ut laoreet tortor egestas.
        
    Aliquam at urna vel velit cursus varius sit amet dapibus nulla. Vivamus id nibh sem. Integer faucibus, turpis nec interdum suscipit, mauris libero malesuada diam, quis elementum odio augue vel est. Ut ut leo porta, feugiat tellus eget, rutrum ex. Aenean rhoncus ante augue, vitae pharetra eros dignissim et. In blandit augue risus, eu interdum est euismod vitae. Donec id lobortis augue. Mauris consectetur, ligula vel maximus molestie, nunc felis tempus odio, sagittis cursus justo sapien eu mauris. Praesent pellentesque cursus odio, in elementum ex mollis eu. Nullam eu ligula ac turpis tempus efficitur.
        
    Mauris tempus, velit vitae tincidunt congue, magna magna maximus ligula, ut dignissim neque mi eu eros. Curabitur tincidunt eget massa fermentum vulputate. Curabitur fringilla lectus et libero auctor, et scelerisque mauris rutrum. Phasellus mollis, magna in aliquam porttitor, sem mi vestibulum magna, nec sollicitudin diam ligula at eros. Ut et nulla eget risus malesuada viverra. Sed interdum felis non nibh ullamcorper pulvinar. Duis vitae turpis sed neque luctus pharetra. Nulla pharetra massa vel lectus faucibus sodales. Fusce molestie erat id bibendum accumsan. Etiam sed felis quis neque ullamcorper ultricies. Curabitur id lorem luctus dui varius ultricies. Sed at velit in elit tristique eleifend vel ac dui. Cras tristique feugiat pellentesque. Duis at enim hendrerit, tincidunt erat a, pretium nisi. Ut nec egestas felis. Ut lobortis lobortis mi ut lacinia.
        
    Pellentesque porttitor quis purus eu imperdiet. Phasellus at lectus bibendum, eleifend felis id, vehicula lacus. Aenean a orci dolor. Phasellus eu hendrerit justo. Morbi rhoncus aliquam sapien et volutpat. Aenean in viverra eros, ac mollis nisl. Vivamus cursus dolor justo, at imperdiet felis molestie commodo. Etiam eleifend ante quam, eget blandit quam consequat congue. Sed in est laoreet massa porttitor tempus sed in augue.
        
    Donec convallis faucibus nibh, ut pellentesque justo venenatis eget. Curabitur vel mollis erat. Nulla consectetur pretium risus id tincidunt. Cras bibendum interdum mattis. Mauris varius sem et sem volutpat porttitor. Etiam condimentum purus ut venenatis viverra. Maecenas aliquam lorem at enim auctor, sit amet interdum odio fermentum. Donec sapien felis, interdum et eros sed, accumsan elementum lacus. Donec bibendum ornare nunc et pellentesque. Proin hendrerit rhoncus dignissim. Sed non velit erat.
        
    Pellentesque non rutrum neque, ac posuere sapien. Morbi laoreet turpis urna, et mattis elit scelerisque ornare. Ut euismod odio a faucibus maximus. Ut molestie eleifend nisl vel tristique. Morbi vel ligula sagittis, scelerisque quam id, tincidunt urna. Donec vel efficitur eros. Etiam a turpis auctor, pretium nisl at, lacinia quam. Aenean mollis, tellus id tempus pharetra, ex turpis consequat nibh, sit amet pellentesque tellus elit vitae elit. Praesent a hendrerit sem. Phasellus cursus bibendum placerat. Praesent feugiat porta lorem sed feugiat. Aliquam vulputate pharetra tortor at mattis. Nulla elementum vitae orci in feugiat. Curabitur metus odio, rhoncus sed ligula id, vulputate porta lacus. Quisque tempus finibus vehicula."""

    users = []
    users.append(User(certificate=values["uid1"], name=values["name1"]))
    users.append(User(certificate=values["uid2"], name=values["name2"]))
    users.append(User(certificate=values["uid3"], name=values["name3"]))
    for user in users:
        user.threads.append(Thread(heading=values["heading1"], body=values["body1"]))
        user.threads.append(Thread(heading=values["heading2"], body=values["body2"]))
    for user in users:
        for thread in user.threads:
            thread.replies.append(Comment(user=users[0], body=values["body1"]))
            thread.replies.append(Comment(user=users[1], body=values["body2"]))
            thread.replies.append(Comment(user=users[2], body=values["body3"]))

    files = [File(name=values["fname1"], url=["url1"]), File(name=values["fname2"], url=["url2"]), File(name=values["fname3"], url=["url3"])]
    for user, upload in zip(users, files):
        user.uploads.append(upload)

    for user in users:
        for thread in user.threads:
            for upload in files:
                thread.attachments.append(upload)
        for comment in user.comments:
            for upload in files:
                comment.attachments.append(upload)

    for user in users:
        session.add(user)




if __name__ == "__main__":
    sessionMgr = SessionManager("postgres","password","localhost", debug=True)
    with sessionMgr.session_scope() as session:
        dropSchema(sessionMgr.engine)
        declareSchema(sessionMgr.engine)
        populate(session)

