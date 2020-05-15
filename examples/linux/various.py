""" A few drgn functions similar to crash """

from drgn.helpers.linux.pid import for_each_task
from drgn.helpers.linux.pid import for_each_task
from curses.ascii import isprint

""" Equivalent of ps -l in crash """
def psl():
     taskstate={128:"ZO",260:"ST",1026:"ID",1:"IN",2:"UN",0:"RU"}
     for task in sorted(for_each_task(prog), key=lambda prog: prog.sched_info.last_arrival, reverse=True):
          print(f"[{task.sched_info.last_arrival.value_():>16}] [{taskstate.get(task.state.value_())}] PID: {task.pid.value_():<6} TASK: {hex(task)} CPU: {task.cpu.value_():<2} COMMAND: \"{task.comm.string_().decode()}\"")

""" Get a per-cpu object given the variable name and CPU number """
def getpcptr(vname,cpu):
     offset=prog["__per_cpu_offset"][cpu].value_()
     obj=Object(prog, prog[vname].type_, address=offset+prog[vname].address_)
     return obj

""" Friendly check for variable """
def getv(vname):
     try:
        s=prog[vname]
     except:
        print(f"symbol not found {vname}")
        return
     return s

""" Dump memory """
def mdump(start, length):
       theend=start+length
       while start<=theend:
           v1=prog.read_u64(start)
           v2=prog.read_u64(start+8)
           str=""
           for i in range(16):
               v=prog.read_u8(start+i)
               if isprint(v):
                   str=str+chr(v)
               else:
                   str=str+"."
               if i==7:
                   str=str+" "
           print(f"[{start:#018x}]:    {v1:#018x} {v2:#018x}  {str}")
           start=start+16

""" Print a backtrace with more details if expand set"""
def pbt(task, expand):
     laststack=0
     try:
        print("")
        print("PID:", task.pid.value_(), "  ", task.comm.string_().decode())
        fn=0
        for fr in prog.stack_trace(task.pid.value_()):
           pc=fr.pc
           sp=fr.register('rsp')
           try:
               sym=prog.symbol(fr.pc).name
               offset=fr.pc-prog.symbol(fr.pc).address
               siz=prog.symbol(fr.pc).size
           except LookupError:
               sym="unknown"
               offset=0
               siz=0
           if expand==1 and laststack!=0 and (sp-laststack)<1000:
               while laststack<=sp:
                   v1=prog.read_u64(laststack)
                   v2=prog.read_u64(laststack+8)
                   print(f"   [{laststack:#018x}]:    {v1:#018x} {v2:#018x}")
                   laststack=laststack+16
           laststack=sp
           print(f"#{fn} [{sp:#016x}] {sym} at {hex(pc)}+{hex(offset)}/{hex(siz)}")
           fn=fn+1
     except:
        pass

""" Print all backtraces basic """
def pbtall():
     for task in for_each_task(prog):
          pbt(task,0)

""" Print all backtraces detailed """
def pbtallf():
     for task in for_each_task(prog):
          pbt(task,1)
