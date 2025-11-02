import { useCallback, useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
 Table,
 TableBody,
 TableCell,
 TableHead,
 TableHeader,
 TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Search, MoreVertical, UserX, UserCheck, Eye } from "lucide-react";
import {
 DropdownMenu,
 DropdownMenuContent,
 DropdownMenuItem,
 DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
  // TODO: Replace apiClient calls with generated hooks from '@/lib/api/generated'
import { AdminUser } from "@/types/admin";
import { toast } from "sonner";
import { UserDetailsDialog } from "./UserDetails";

export default function AdminUsers() {
 const [users, setUsers] = useState<AdminUser[]>([]);
 const [isLoading, setIsLoading] = useState(true);
 const [searchInput, setSearchInput] = useState("");
 const [query, setQuery] = useState("");
 const [page, setPage] = useState(1);
 const [selectedUserId, setSelectedUserId] = useState<string | null>(null);

 const fetchUsers = useCallback(async (pageToFetch: number, searchTerm: string) => {
 setIsLoading(true);
 try {
 const data = await apiClient.getUsers(pageToFetch, searchTerm);
 setUsers(data.users || []);
 } catch (error) {
 toast.error("Failed to load users");
 console.error(error);
 } finally {
 setIsLoading(false);
 }
 }, []);

 useEffect(() => {
 void fetchUsers(page, query);
 }, [page, query, fetchUsers]);

 const handleSearch = () => {
 setPage(1);
 setQuery(searchInput);
 void fetchUsers(1, searchInput);
 };

 const handleStatusChange = async (userId: string, newStatus: "active" | "suspended") => {
 try {
 await apiClient.updateUserStatus(userId, newStatus);
 toast.success(`User ${newStatus === "active" ? "activated" : "suspended"}`);
 void fetchUsers(page, query);
 } catch (error) {
 toast.error("Failed to update user status");
 console.error(error);
 }
 };

 return (
 <div className="p-8 space-y-6">
 <div>
 <h1 className="text-3xl font-bold gradient-text-primary flex items-center gap-3">
 <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center shadow-lg shadow-primary/20">
 <Search className="w-6 h-6 text-primary-foreground" />
 </div>
 User Management
 </h1>
 <p className="text-muted-foreground mt-2">View and manage all registered users</p>
 </div>

 <div className="flex gap-4">
 <div className="relative flex-1">
 <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-primary z-10" />
 <Input
 placeholder="Search by email or name..."
 value={searchInput}
 onChange={(e) => setSearchInput(e.target.value)}
 onKeyDown={(e) => e.key === "Enter" && handleSearch()}
 className="pl-11 border-primary/30 focus:border-primary/60 focus:ring-primary/20"
 />
 </div>
 <Button 
 onClick={handleSearch}
 className="bg-primary hover:opacity-90 text-primary-foreground shadow-lg shadow-primary/30 hover:shadow-xl hover:shadow-primary/40 hover:-translate-y-0.5 px-8"
 >
 <Search className="w-4 h-4 mr-2" />
 Search
 </Button>
 </div>

 <div className="bg-surface border border-primary/20 rounded-lg shadow-lg overflow-hidden">
 <Table>
 <TableHeader>
 <TableRow className="bg-surface border-b border-primary/20 hover:bg-surface hover: hover:">
 <TableHead className="text-primary font-bold">User</TableHead>
 <TableHead className="text-primary font-bold">Email</TableHead>
 <TableHead className="text-primary font-bold">Status</TableHead>
 <TableHead className="text-primary font-bold">Credits</TableHead>
 <TableHead className="text-primary font-bold">Joined</TableHead>
 <TableHead className="text-primary font-bold">Last Login</TableHead>
 <TableHead className="text-right text-primary font-bold">Actions</TableHead>
 </TableRow>
 </TableHeader>
 <TableBody>
 {isLoading ? (
 <TableRow>
 <TableCell colSpan={7} className="text-center py-8">
 Loading users...
 </TableCell>
 </TableRow>
 ) : users.length === 0 ? (
 <TableRow>
 <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
 No users found
 </TableCell>
 </TableRow>
 ) : (
 users.map((user, idx) => (
 <TableRow 
 key={user.id}
 className={`transition-colors border-b border-border/30 ${idx % 2 === 0 ? 'hover:bg-primary/5' : 'hover:bg-accent/5'}`}
 >
 <TableCell className="font-semibold text-foreground">{user.name}</TableCell>
 <TableCell className="text-foreground">{user.email}</TableCell>
 <TableCell>
 <Badge 
 variant={user.status === "active" ? "default" : "danger"}
 className="font-semibold"
 >
 {user.status === "active" ? (
 <span className="flex items-center gap-1">
 <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
 {user.status}
 </span>
 ) : (
 user.status
 )}
 </Badge>
 </TableCell>
 <TableCell>
 <span className="font-bold text-primary">{user.credits}</span>
 </TableCell>
 <TableCell className="text-muted-foreground">{new Date(user.created_at).toLocaleDateString()}</TableCell>
 <TableCell className="text-muted-foreground">
 {user.last_login ? new Date(user.last_login).toLocaleDateString() : <span className="text-muted-foreground/60">Never</span>}
 </TableCell>
 <TableCell className="text-right">
 <DropdownMenu>
 <DropdownMenuTrigger asChild>
 <Button 
 variant="ghost" 
 size="sm"
 className="hover:bg-primary/20 hover:text-primary border border-transparent hover:border-primary/30"
 >
 <MoreVertical className="h-4 w-4" />
 </Button>
 </DropdownMenuTrigger>
 <DropdownMenuContent align="end" className="bg-card border-primary/20">
 <DropdownMenuItem
 className="hover:bg-primary/10 hover:text-primary cursor-pointer"
 onSelect={(event) => {
 event.preventDefault();
 setSelectedUserId(user.id);
 }}
 >
 <Eye className="mr-2 h-4 w-4 text-primary" />
 View Details
 </DropdownMenuItem>
 {user.status === "active" ? (
 <DropdownMenuItem
 className="text-danger hover:bg-danger/10 cursor-pointer"
 onSelect={(event) => {
 event.preventDefault();
 void handleStatusChange(user.id, "suspended");
 }}
 >
 <UserX className="mr-2 h-4 w-4" />
 Suspend User
 </DropdownMenuItem>
 ) : (
 <DropdownMenuItem
 className="text-success hover:bg-success/10 cursor-pointer"
 onSelect={(event) => {
 event.preventDefault();
 void handleStatusChange(user.id, "active");
 }}
 >
 <UserCheck className="mr-2 h-4 w-4" />
 Activate User
 </DropdownMenuItem>
 )}
 </DropdownMenuContent>
 </DropdownMenu>
 </TableCell>
 </TableRow>
 ))
 )}
 </TableBody>
 </Table>
 </div>

 <div className="flex justify-between items-center">
 <Button
 variant="outline"
 onClick={() => {
 const nextPage = Math.max(1, page - 1);
 setPage(nextPage);
 }}
 disabled={page === 1}
 className="border-primary/30 hover:bg-primary hover:text-primary-foreground hover:border-primary/50 disabled:opacity-50 disabled:cursor-not-allowed"
 >
 Previous
 </Button>
 <span className="text-sm font-semibold text-primary px-4 py-2 bg-primary/10 rounded-lg border border-primary/20">
 Page {page}
 </span>
 <Button
 variant="outline"
 onClick={() => {
 const nextPage = page + 1;
 setPage(nextPage);
 }}
 className="border-accent/30 hover:bg-accent hover:text-accent-foreground hover:border-accent/50"
 >
 Next
 </Button>
 </div>

 <UserDetailsDialog
 userId={selectedUserId || ""}
 isOpen={Boolean(selectedUserId)}
 onClose={() => setSelectedUserId(null)}
 />
 </div>
 );
}
